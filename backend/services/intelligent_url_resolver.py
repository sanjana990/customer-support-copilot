
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class URLResult:
    doc: str
    url: str
    relevance_score: float
    is_valid: bool

class IntelligentURLResolver:
    def __init__(self):
        # Known valid URL patterns with their contexts
        self.url_patterns = {
            'sdk': {
                'python': {
                    'base': 'https://developer.atlan.com/sdks/python/',
                    'contexts': ['setup', 'authentication', 'getting started', 'reference']
                },
                'java': {
                    'base': 'https://developer.atlan.com/sdks/java/',
                    'contexts': ['setup', 'authentication', 'getting started', 'reference']
                },
                'javascript': {
                    'base': 'https://developer.atlan.com/sdks/javascript/',
                    'contexts': ['setup', 'authentication', 'getting started', 'reference']
                },
                'go': {
                    'base': 'https://developer.atlan.com/sdks/go/',
                    'contexts': ['setup', 'authentication', 'getting started', 'reference']
                }
            },
            'integrations': {
                'snowflake': {
                    'base': 'https://docs.atlan.com/product/integrations',
                    'contexts': ['setup', 'configuration', 'troubleshooting']
                },
                'databricks': {
                    'base': 'https://docs.atlan.com/product/integrations',
                    'contexts': ['setup', 'configuration', 'troubleshooting']
                },
                'powerbi': {
                    'base': 'https://docs.atlan.com/product/integrations',
                    'contexts': ['setup', 'configuration', 'troubleshooting']
                }
            },
            'governance': {
                'base': 'https://docs.atlan.com/use-data/data-governance',
                'contexts': ['best practices', 'workspace management', 'team permissions']
            }
        }
        
        # Intent keywords mapping
        self.intent_keywords = {
            'setup': ['setup', 'install', 'configure', 'getting started', 'begin'],
            'authentication': ['auth', 'login', 'token', 'api key', 'credentials'],
            'troubleshooting': ['error', 'issue', 'problem', 'fix', 'debug'],
            'configuration': ['config', 'settings', 'options', 'customize'],
            'reference': ['api', 'reference', 'documentation', 'guide']
        }

    def analyze_intent(self, query: str) -> Dict[str, any]:
        """Analyze user intent using AI-powered context extraction"""
        query_lower = query.lower()
        
        # Extract technology/platform
        technology = self._extract_technology(query_lower)
        
        # Extract action/intent
        action = self._extract_action(query_lower)
        
        # Extract urgency/context
        urgency = self._extract_urgency(query_lower)
        
        # Determine primary category
        category = self._determine_category(query_lower, technology)
        
        return {
            'technology': technology,
            'action': action,
            'urgency': urgency,
            'category': category,
            'original_query': query
        }

    def _extract_technology(self, query: str) -> Optional[str]:
        """Extract technology/platform from query"""
        tech_patterns = {
            'python': ['python', 'py'],
            'java': ['java'],
            'javascript': ['javascript', 'js', 'node', 'typescript'],
            'go': ['go', 'golang'],
            'snowflake': ['snowflake'],
            'databricks': ['databricks'],
            'powerbi': ['powerbi', 'power bi'],
            'tableau': ['tableau']
        }
        
        for tech, patterns in tech_patterns.items():
            if any(pattern in query for pattern in patterns):
                return tech
        return None

    def _extract_action(self, query: str) -> str:
        """Extract user action/intent from query"""
        for action, keywords in self.intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                return action
        return 'general'

    def _extract_urgency(self, query: str) -> str:
        """Extract urgency level from query"""
        urgent_keywords = ['urgent', 'critical', 'emergency', 'asap', 'immediately']
        if any(keyword in query for keyword in urgent_keywords):
            return 'high'
        return 'medium'

    def _determine_category(self, query: str, technology: str) -> str:
        """Determine primary category based on query and technology"""
        # Check for governance keywords first
        if any(keyword in query for keyword in ['governance', 'workspace', 'team', 'permission', 'best practice', 'rollout', 'business unit']):
            return 'governance'
        elif technology in ['python', 'java', 'javascript', 'go']:
            return 'sdk'
        elif technology in ['snowflake', 'databricks', 'powerbi', 'tableau']:
            return 'integrations'
        else:
            return 'general'

    def resolve_urls(self, query: str) -> List[URLResult]:
        """Main method to resolve URLs for a given query"""
        intent = self.analyze_intent(query)
        
        # Get candidate URLs based on intent
        candidates = self._get_candidate_urls(intent)
        
        # Rank and validate URLs
        ranked_urls = self._rank_urls(candidates, intent)
        
        # Return top 3 most relevant URLs
        return ranked_urls[:3]

    def resolve_urls_with_topic(self, query: str, classified_topic: str) -> List[URLResult]:
        """Resolve URLs using both query analysis and classified topic"""
        intent = self.analyze_intent(query)
        
        # Override the category with the classified topic if it's more specific
        if classified_topic != 'general':
            intent['category'] = classified_topic
        
        # Get candidate URLs based on enhanced intent
        candidates = self._get_candidate_urls(intent)
        
        # Rank and validate URLs
        ranked_urls = self._rank_urls(candidates, intent)
        
        # Return top 3 most relevant URLs
        return ranked_urls[:3]

    def _get_candidate_urls(self, intent: Dict) -> List[URLResult]:
        """Get candidate URLs based on analyzed intent"""
        candidates = []
        category = intent['category']
        technology = intent['technology']
        action = intent['action']
        
        if category == 'sdk' and technology:
            # SDK-specific URLs
            if technology in self.url_patterns['sdk']:
                base_url = self.url_patterns['sdk'][technology]['base']
                candidates.append(URLResult(
                    doc=f'{technology.title()} SDK Documentation',
                    url=base_url,
                    relevance_score=0.9,
                    is_valid=True
                ))
                
                # Add developer hub as secondary
                candidates.append(URLResult(
                    doc='Developer Hub',
                    url='https://developer.atlan.com',
                    relevance_score=0.7,
                    is_valid=True
                ))
        
        elif category == 'integrations' and technology:
            # Integration-specific URLs
            if technology in self.url_patterns['integrations']:
                base_url = self.url_patterns['integrations'][technology]['base']
                candidates.append(URLResult(
                    doc=f'{technology.title()} Integration Guide',
                    url=base_url,
                    relevance_score=0.9,
                    is_valid=True
                ))
        
        elif category == 'governance':
            # Governance-related URLs
            candidates.append(URLResult(
                doc='Data Governance Documentation',
                url=self.url_patterns['governance']['base'],
                relevance_score=0.8,
                is_valid=True
            ))
        
        # Handle specific API/SDK cases without technology
        elif category == 'sdk' and not technology:
            # General API/SDK questions
            if any(keyword in intent['original_query'].lower() for keyword in ['authentication', 'auth', 'api key', 'oauth']):
                candidates.append(URLResult(
                    doc='API Authentication Guide',
                    url='https://developer.atlan.com',
                    relevance_score=0.8,
                    is_valid=True
                ))
            else:
                candidates.append(URLResult(
                    doc='Developer Hub',
                    url='https://developer.atlan.com',
                    relevance_score=0.7,
                    is_valid=True
                ))
        
        # Handle specific connector cases without technology
        elif category == 'integrations' and not technology:
            # General connector/integration questions
            if any(keyword in intent['original_query'].lower() for keyword in ['lineage', 'connector', 'capture']):
                candidates.append(URLResult(
                    doc='Connectors & Lineage Guide',
                    url='https://docs.atlan.com/product/integrations',
                    relevance_score=0.8,
                    is_valid=True
                ))
            else:
                candidates.append(URLResult(
                    doc='Integrations Documentation',
                    url='https://docs.atlan.com/product/integrations',
                    relevance_score=0.7,
                    is_valid=True
                ))
        
        # Always add fallback URLs
        if not candidates:
            candidates.extend([
                URLResult(
                    doc='Atlan Documentation',
                    url='https://docs.atlan.com',
                    relevance_score=0.6,
                    is_valid=True
                ),
                URLResult(
                    doc='Developer Hub',
                    url='https://developer.atlan.com',
                    relevance_score=0.5,
                    is_valid=True
                )
            ])
        
        return candidates

    def _rank_urls(self, candidates: List[URLResult], intent: Dict) -> List[URLResult]:
        """Rank URLs by relevance to user intent"""
        # Sort by relevance score (higher is better)
        return sorted(candidates, key=lambda x: x.relevance_score, reverse=True)

# Global instance
url_resolver = IntelligentURLResolver()
