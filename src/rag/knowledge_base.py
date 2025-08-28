"""
RAG (Retrieval-Augmented Generation) 지식베이스
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """재무관리 지식베이스 클래스"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.documents = []
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """지식베이스 초기화"""
        try:
            logger.info("지식베이스 초기화 시작...")
            
            # OpenAI 임베딩 초기화
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("AOAI_API_KEY"),
                openai_api_base=os.getenv("AOAI_ENDPOINT"),
                openai_api_version="2024-02-15-preview",
                deployment=os.getenv("AOAI_DEPLOY_EMBED_3_SMALL")
            )
            
            # 문서 로드
            self._load_documents()
            
            # 벡터 스토어 생성
            self._create_vector_store()
            
            self.is_initialized = True
            logger.info("지식베이스 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"지식베이스 초기화 실패: {e}")
            return False
    
    def _load_documents(self):
        """문서 로드"""
        try:
            # 재무 지식 문서 로드
            knowledge_file = Path("data/financial_knowledge.txt")
            if knowledge_file.exists():
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 문서 분할
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
                )
                
                chunks = text_splitter.split_text(content)
                
                # Document 객체 생성
                self.documents = [
                    Document(
                        page_content=chunk,
                        metadata={"source": "financial_knowledge.txt", "type": "financial_advice"}
                    )
                    for chunk in chunks
                ]
                
                logger.info(f"{len(self.documents)}개의 문서 청크 로드 완료")
            else:
                logger.warning("재무 지식 파일을 찾을 수 없습니다.")
                
        except Exception as e:
            logger.error(f"문서 로드 실패: {e}")
    
    def _create_vector_store(self):
        """벡터 스토어 생성"""
        try:
            if self.documents and self.embeddings:
                # FAISS 벡터 스토어 생성
                self.vector_store = FAISS.from_documents(
                    self.documents,
                    self.embeddings
                )
                
                # 벡터 스토어 저장
                self.vector_store.save_local("data/vector_store")
                logger.info("벡터 스토어 생성 및 저장 완료")
            else:
                logger.warning("문서 또는 임베딩이 없어 벡터 스토어를 생성할 수 없습니다.")
                
        except Exception as e:
            logger.error(f"벡터 스토어 생성 실패: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """관련 문서 검색"""
        try:
            if not self.is_initialized or not self.vector_store:
                logger.warning("지식베이스가 초기화되지 않았습니다.")
                return []
            
            # 유사도 검색
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"'{query}'에 대한 {len(docs)}개 문서 검색 완료")
            return docs
            
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}")
            return []
    
    def get_relevant_context(self, query: str, max_length: int = 2000) -> str:
        """관련 컨텍스트 추출"""
        try:
            docs = self.search(query, k=3)
            
            if not docs:
                return ""
            
            # 컨텍스트 조합
            context_parts = []
            current_length = 0
            
            for doc in docs:
                content = doc.page_content
                if current_length + len(content) <= max_length:
                    context_parts.append(content)
                    current_length += len(content)
                else:
                    break
            
            context = "\n\n".join(context_parts)
            return context
            
        except Exception as e:
            logger.error(f"컨텍스트 추출 실패: {e}")
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """지식베이스 통계"""
        return {
            "is_initialized": self.is_initialized,
            "document_count": len(self.documents),
            "vector_store_exists": self.vector_store is not None
        }
    
    def get_sample_queries(self) -> List[str]:
        """샘플 쿼리 목록"""
        return [
            "예산 관리는 어떻게 해야 하나요?",
            "투자 포트폴리오를 어떻게 구성해야 하나요?",
            "세금 절약 방법을 알려주세요",
            "은퇴 준비는 언제부터 시작해야 하나요?",
            "비상금은 얼마나 준비해야 하나요?",
            "자산 배분 원칙은 무엇인가요?",
            "연금 상품에는 어떤 것들이 있나요?",
            "부채 관리는 어떻게 해야 하나요?"
        ]
