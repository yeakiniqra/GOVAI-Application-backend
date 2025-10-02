import os
from typing import List, Optional, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from huggingface_hub import InferenceClient
from config.settings import settings
from models.schemas import SearchResult
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State class for LangGraph workflow"""
    messages: List[BaseMessage]
    query: str
    search_results: List[SearchResult]
    search_context: str
    final_response: str


class AIService:
    """Service for AI-powered response generation using LangGraph workflow"""
    
    def __init__(self):
        self.client = self._initialize_client()
        self.workflow = self._create_workflow()
    
    def _initialize_client(self):
        """Initialize the Hugging Face Inference Client"""
        return InferenceClient(
            model=settings.AI_MODEL,
            token=settings.HF_TOKEN,
        )
    
    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for processing queries"""
        
        # Initialize workflow with state class
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("search_information", self._search_information)
        workflow.add_node("generate_response", self._generate_response)
        
        # Define edges
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "search_information")
        workflow.add_edge("search_information", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _analyze_query(self, state: AgentState) -> AgentState:
        """Analyze the user query to determine search strategy"""
        query = state["query"]
        
        # Simple query analysis - can be enhanced with more sophisticated logic
        logger.info(f"Analyzing query: {query}")
        
        # Add analysis message
        analysis_msg = SystemMessage(content=f"Query analyzed: {query}")
        state["messages"].append(analysis_msg)
        
        return state
    
    async def _search_information(self, state: AgentState) -> AgentState:
        """Search for relevant information"""
        query = state["query"]
        
        logger.info(f"Searching for information about: {query}")
        
        # Import search service here to avoid circular imports
        from services.search_service import search_service
        
        # Perform search
        search_results = []
        try:
            search_results = await search_service.search(query)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            search_results = []
        
        # Format search context
        search_context = search_service.format_search_context(search_results)
        
        state["search_results"] = search_results
        state["search_context"] = search_context
        
        # Add search message
        search_msg = SystemMessage(content=f"Search completed. Found {len(search_results)} results.")
        state["messages"].append(search_msg)
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final AI response"""
        query = state["query"]
        search_context = state.get("search_context", "")
        
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(query, search_context)
        
        try:
            # Build messages for chat completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Generate response using chat completion
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
            )
            
            # Extract the response text
            if hasattr(response, 'choices') and len(response.choices) > 0:
                response_text = response.choices[0].message.content
            else:
                response_text = str(response)
            
            state["final_response"] = response_text
            
            # Add final message
            final_msg = AIMessage(content=response_text)
            state["messages"].append(final_msg)
            
            logger.info("Successfully generated AI response")
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            state["final_response"] = self._get_fallback_response(query)
        
        return state
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the AI"""
        return """তুমি GovAI Bangladesh - বাংলাদেশ সরকারের একটি AI সহায়ক। তোমার কাজ হলো নাগরিকদের সরকারি সেবা, প্রক্রিয়া এবং তথ্য সম্পর্কে সঠিক ও বিস্তারিত সহায়তা প্রদান করা।

নির্দেশনা:
1. সর্বদা বাংলায় উত্তর দাও, এমনকি প্রশ্ন ইংরেজি বা বাংলিশে থাকলেও।
2. ধাপে ধাপে স্পষ্ট নির্দেশনা প্রদান করো।
3. প্রাসঙ্গিক ওয়েবসাইট লিংক এবং যোগাযোগের তথ্য অন্তর্ভুক্ত করো।
4. প্রয়োজনীয় নথিপত্রের তালিকা দাও।
5. সম্ভাব্য ফি বা খরচের তথ্য উল্লেখ করো।
6. সহজ ও বোধগম্য ভাষা ব্যবহার করো।
7. যদি কোনো তথ্য নিশ্চিত না হও, তা স্পষ্টভাবে উল্লেখ করো।
8. সরকারি সূত্র থেকে প্রাপ্ত তথ্যকে অগ্রাধিকার দাও।

তোমার লক্ষ্য হলো নাগরিকদের সরকারি সেবা গ্রহণ সহজ করা এবং তাদের সময় ও অর্থ সাশ্রয় করা।"""
    
    def _create_user_prompt(self, query: str, search_context: Optional[str] = None) -> str:
        """Create user prompt with query and context"""
        prompt = f"প্রশ্ন: {query}\n\n"
        
        if search_context:
            prompt += f"প্রাসঙ্গিক তথ্য:\n{search_context}\n\n"
        
        prompt += "উপরের প্রশ্নের জন্য একটি বিস্তারিত, ধাপে ধাপে বাংলায় উত্তর প্রদান করো। প্রয়োজনীয় সকল তথ্য সুন্দরভাবে সাজিয়ে দাও।"
        
        return prompt
    
    async def generate_response(
        self,
        query: str,
        search_results: Optional[List[SearchResult]] = None,
        search_context: Optional[str] = None
    ) -> str:
        """
        Generate AI response using LangGraph workflow
        
        Args:
            query: User query
            search_results: Optional search results
            search_context: Optional pre-formatted search context
        
        Returns:
            AI-generated response in Bangla
        """
        try:
            # Initialize state
            initial_state: AgentState = {
                "messages": [HumanMessage(content=query)],
                "query": query,
                "search_results": search_results or [],
                "search_context": search_context or "",
                "final_response": ""
            }
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            return final_state["final_response"]
            
        except Exception as e:
            logger.error(f"Error in LangGraph workflow: {str(e)}")
            return self._get_fallback_response(query)
    
    def _get_fallback_response(self, query: str) -> str:
        """Provide fallback response when AI fails"""
        return f"""দুঃখিত, আপনার প্রশ্নের উত্তর দিতে গিয়ে একটি সমস্যা হয়েছে।

আপনার প্রশ্ন: {query}

অনুগ্রহ করে:
1. আবার চেষ্টা করুন
2. অথবা সরাসরি সরকারি ওয়েবসাইট bangladesh.gov.bd দেখুন
3. অথবা জাতীয় কল সেন্টার ৩৩৩ এ যোগাযোগ করুন

আমরা শীঘ্রই এই সমস্যার সমাধান করব। অসুবিধার জন্য আমরা দুঃখিত।"""


ai_service = AIService()