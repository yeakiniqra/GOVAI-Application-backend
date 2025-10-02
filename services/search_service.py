from typing import List, Optional, Dict, Any
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import BaseTool
from config.settings import settings
from models.schemas import SearchResult
import logging
import asyncio

# Use the new tavily import
try:
    from langchain_tavily import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.tools import TavilySearchResults
        TAVILY_AVAILABLE = True
    except ImportError:
        TAVILY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SearchService:
    """Service for search using LangChain tools"""
    
    def __init__(self):
        self.max_results = settings.SEARCH_MAX_RESULTS
        self.search_tool = self._initialize_search_tool()
        self._log_search_config()
    
    def _log_search_config(self):
        """Log search configuration status"""
        if self.search_tool:
            tool_name = self.search_tool.__class__.__name__
            logger.info(f"✓ Search tool initialized: {tool_name}")
        else:
            logger.warning("✗ No search API configured!")
            logger.warning("Add TAVILY_API_KEY or SERPAPI_API_KEY to .env file")
            logger.warning("Get Tavily key: https://tavily.com/")
            logger.warning("Get SerpAPI key: https://serpapi.com/")
    
    def _initialize_search_tool(self) -> Optional[BaseTool]:
        """Initialize the best available search tool"""
        
        # Check which API keys are available
        has_tavily = bool(settings.TAVILY_API_KEY)
        has_serpapi = bool(settings.SERPAPI_API_KEY)
        
        logger.info(f"Tavily API key available: {has_tavily}")
        logger.info(f"SerpAPI key available: {has_serpapi}")
        
        if not has_tavily and not has_serpapi:
            logger.error("No search API keys found in settings!")
            logger.error("Please add TAVILY_API_KEY or SERPAPI_API_KEY to your .env file")
            return None
        
        try:
            # Try Tavily first (if API key is available and library is installed)
            if has_tavily and TAVILY_AVAILABLE:
                logger.info("Attempting to initialize Tavily search...")
                try:
                    tool = TavilySearchResults(
                        max_results=self.max_results,
                        tavily_api_key=settings.TAVILY_API_KEY,  # Use explicit parameter name
                        search_depth="advanced"
                    )
                    logger.info("✓ Tavily initialized successfully")
                    return tool
                except Exception as e:
                    logger.error(f"✗ Tavily initialization failed: {str(e)}")
            
            # Fallback to SerpAPI
            if has_serpapi:
                logger.info("Attempting to initialize SerpAPI search...")
                try:
                    serpapi = SerpAPIWrapper(
                        serpapi_api_key=settings.SERPAPI_API_KEY,
                        params={
                            "num": self.max_results,
                            "hl": "bn",  # Bengali language
                            "gl": "bd"   # Bangladesh location
                        }
                    )
                    logger.info("✓ SerpAPI initialized successfully")
                    return serpapi
                except Exception as e:
                    logger.error(f"✗ SerpAPI initialization failed: {str(e)}")
            
            logger.error("All search tool initialization attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error initializing search tool: {str(e)}")
            return None
    
    async def search(self, query: str, language: str = "bn") -> List[SearchResult]:
        """
        Perform search using LangChain tools
        
        Args:
            query: Search query
            language: Language code (bn for Bangla, en for English)
        
        Returns:
            List of search results
        """
        if not self.search_tool:
            logger.warning("No search tool available - using fallback results")
            return self._get_fallback_results(query)
        
        try:
            # Add Bangladesh government context to improve relevance
            enhanced_query = f"{query} Bangladesh government official site:gov.bd OR site:bangladesh.gov.bd"
            
            logger.info(f"Searching for: {enhanced_query}")
            
            # Execute search
            if isinstance(self.search_tool, TavilySearchResults):
                results = await self._search_with_tavily(enhanced_query)
            else:
                results = await self._search_with_serpapi(enhanced_query)
            
            logger.info(f"Found {len(results)} search results for query: {query}")
            return results if results else self._get_fallback_results(query)
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return self._get_fallback_results(query)
    
    async def _search_with_tavily(self, query: str) -> List[SearchResult]:
        """Search using Tavily"""
        try:
            # Run in thread pool since Tavily might be synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self.search_tool.run, query)
            
            search_results = []
            for item in results:
                if isinstance(item, dict):
                    search_results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        score=item.get("score", 0.0)
                    ))
            
            return search_results[:self.max_results]
            
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    async def _search_with_serpapi(self, query: str) -> List[SearchResult]:
        """Search using SerpAPI"""
        try:
            # Run in thread pool since SerpAPI might be synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self.search_tool.run, query)
            
            search_results = []
            # Parse SerpAPI results format
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        search_results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            score=1.0  # SerpAPI doesn't provide scores
                        ))
            elif isinstance(results, dict):
                # Handle alternative SerpAPI response format
                organic_results = results.get("organic_results", [])
                for item in organic_results:
                    if isinstance(item, dict):
                        search_results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            score=1.0
                        ))
            
            return search_results[:self.max_results]
            
        except Exception as e:
            logger.error(f"SerpAPI search error: {str(e)}")
            return []
    
    def _get_fallback_results(self, query: str) -> List[SearchResult]:
        """Provide fallback search results when no search tool is available"""
        logger.info("Providing fallback search results")
        
        # Basic fallback results for common government services
        fallback_results = []
        
        query_lower = query.lower()
        
        # Passport related
        if any(keyword in query_lower for keyword in ['পাসপোর্ট', 'passport']):
            fallback_results.append(SearchResult(
                title="পাসপোর্ট আবেদন - বাংলাদেশ সরকার",
                url="https://www.dip.portal.gov.bd/",
                snippet="পাসপোর্ট আবেদনের জন্য প্রয়োজনীয় কাগজপত্র ও প্রক্রিয়া সম্পর্কে বিস্তারিত তথ্য।",
                score=1.0
            ))
        
        # National ID related
        if any(keyword in query_lower for keyword in ['জাতীয় পরিচয়পত্র', 'nid', 'national id']):
            fallback_results.append(SearchResult(
                title="জাতীয় পরিচয়পত্র - নির্বাচন কমিশন",
                url="https://services.nidportal.gov.bd/",
                snippet="জাতীয় পরিচয়পত্র সংশোধন, নতুন আবেদন ও অন্যান্য সেবা।",
                score=1.0
            ))
        
        # Birth certificate related
        if any(keyword in query_lower for keyword in ['জন্ম নিবন্ধন', 'birth certificate', 'birth']):
            fallback_results.append(SearchResult(
                title="জন্ম ও মৃত্যু নিবন্ধন - স্থানীয় সরকার বিভাগ",
                url="https://bdris.gov.bd/",
                snippet="জন্ম ও মৃত্যু নিবন্ধন সংক্রান্ত সকল সেবা।",
                score=1.0
            ))
        
        # Driving license related
        if any(keyword in query_lower for keyword in ['ড্রাইভিং', 'driving', 'license', 'লাইসেন্স']):
            fallback_results.append(SearchResult(
                title="ড্রাইভিং লাইসেন্স - বাংলাদেশ সড়ক পরিবহন কর্তৃপক্ষ",
                url="https://www.brta.gov.bd/",
                snippet="ড্রাইভিং লাইসেন্স আবেদন, রিনিউ এবং সংশোধন সংক্রান্ত সেবা। ফি: নতুন লাইসেন্স ৫০০-১০০০ টাকা, রিনিউ ৫০০ টাকা।",
                score=1.0
            ))
        
        # Tax related
        if any(keyword in query_lower for keyword in ['কর', 'tax', 'tin']):
            fallback_results.append(SearchResult(
                title="জাতীয় রাজস্ব বোর্ড - কর সেবা",
                url="https://www.nbr.gov.bd/",
                snippet="আয়কর, মূল্য সংযোজন কর (ভ্যাট) এবং TIN সংক্রান্ত সকল সেবা।",
                score=1.0
            ))
        
        # Education related
        if any(keyword in query_lower for keyword in ['শিক্ষা', 'education', 'certificate', 'সার্টিফিকেট']):
            fallback_results.append(SearchResult(
                title="শিক্ষা বোর্ড - সার্টিফিকেট সেবা",
                url="https://www.educationboardresults.gov.bd/",
                snippet="শিক্ষা সনদ, ফলাফল এবং সার্টিফিকেট সংক্রান্ত সেবা।",
                score=1.0
            ))
        
        # If no specific results, provide general government portal
        if not fallback_results:
            fallback_results.append(SearchResult(
                title="বাংলাদেশ সরকারের তথ্য বাতায়ন",
                url="https://bangladesh.gov.bd/",
                snippet="বাংলাদেশ সরকারের সকল মন্ত্রণালয় ও বিভাগের তথ্য ও সেবা।",
                score=1.0
            ))
            fallback_results.append(SearchResult(
                title="সেবা প্রদান প্রতিশ্রুতি",
                url="https://services.portal.gov.bd/",
                snippet="সরকারি সকল সেবার তালিকা এবং আবেদন প্রক্রিয়া।",
                score=1.0
            ))
        
        return fallback_results
    
    def format_search_context(self, results: List[SearchResult]) -> str:
        """
        Format search results into context for AI
        
        Args:
            results: List of search results
        
        Returns:
            Formatted context string
        """
        if not results:
            return "কোনো প্রাসঙ্গিক তথ্য পাওয়া যায়নি।"
        
        context = "নিম্নলিখিত তথ্যসূত্র থেকে প্রাপ্ত তথ্য:\n\n"
        for idx, result in enumerate(results, 1):
            context += f"{idx}. {result.title}\n"
            if result.snippet:
                context += f"   বিবরণ: {result.snippet}\n"
            context += f"   লিংক: {result.url}\n\n"
        
        return context


search_service = SearchService()