"""
벡터 데이터베이스 관리 모듈
FAISS와 ChromaDB를 활용한 벡터 저장소 구현
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd

from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from sentence_transformers import SentenceTransformer

from ..core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """벡터 데이터베이스 관리 클래스"""
    
    def __init__(self, store_type: str = "faiss"):
        """
        벡터 저장소 초기화
        
        Args:
            store_type: 저장소 타입 ("faiss" 또는 "chroma")
        """
        self.store_type = store_type
        self.embeddings = self._initialize_embeddings()
        self.vector_store = None
        self.documents = []
        
    def _initialize_embeddings(self):
        """임베딩 모델 초기화"""
        try:
            if settings.use_azure_openai:
                # Azure OpenAI 사용
                return OpenAIEmbeddings(
                    model=settings.aoai_deploy_embed_3_small,
                    openai_api_key=settings.aoai_api_key,
                    openai_api_base=settings.aoai_endpoint,
                    openai_api_version="2024-02-15-preview",
                    deployment=settings.aoai_deploy_embed_3_small
                )
            elif settings.openai_api_key:
                # 일반 OpenAI 사용
                return OpenAIEmbeddings(
                    model=settings.embedding_model,
                    openai_api_key=settings.openai_api_key
                )
            else:
                # OpenAI API 키가 없으면 로컬 모델 사용
                logger.warning("OpenAI API 키가 없어 로컬 임베딩 모델을 사용합니다.")
                return SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 실패: {e}")
            return SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        문서들을 벡터 저장소에 추가
        
        Args:
            documents: 추가할 문서 리스트
        """
        try:
            if not documents:
                logger.warning("추가할 문서가 없습니다.")
                return
            
            self.documents.extend(documents)
            
            if self.store_type == "faiss":
                self._add_to_faiss(documents)
            elif self.store_type == "chroma":
                self._add_to_chroma(documents)
            else:
                raise ValueError(f"지원하지 않는 저장소 타입: {self.store_type}")
                
            logger.info(f"{len(documents)}개 문서가 벡터 저장소에 추가되었습니다.")
            
        except Exception as e:
            logger.error(f"문서 추가 실패: {e}")
            raise
    
    def _add_to_faiss(self, documents: List[Document]) -> None:
        """FAISS에 문서 추가"""
        if self.vector_store is None:
            # 새로운 FAISS 저장소 생성
            self.vector_store = FAISS.from_documents(
                documents, 
                self.embeddings
            )
        else:
            # 기존 저장소에 문서 추가
            self.vector_store.add_documents(documents)
    
    def _add_to_chroma(self, documents: List[Document]) -> None:
        """ChromaDB에 문서 추가"""
        persist_directory = Path(settings.chroma_db_path)
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        if self.vector_store is None:
            # 새로운 ChromaDB 저장소 생성
            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                persist_directory=str(persist_directory)
            )
        else:
            # 기존 저장소에 문서 추가
            self.vector_store.add_documents(documents)
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        유사도 검색 수행
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            filter_dict: 필터 조건
            
        Returns:
            검색된 문서 리스트
        """
        try:
            if self.vector_store is None:
                logger.warning("벡터 저장소가 초기화되지 않았습니다.")
                return []
            
            if self.store_type == "faiss":
                return self.vector_store.similarity_search(query, k=k)
            elif self.store_type == "chroma":
                return self.vector_store.similarity_search(
                    query, 
                    k=k,
                    filter=filter_dict
                )
            else:
                raise ValueError(f"지원하지 않는 저장소 타입: {self.store_type}")
                
        except Exception as e:
            logger.error(f"유사도 검색 실패: {e}")
            return []
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        점수와 함께 유사도 검색 수행
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            filter_dict: 필터 조건
            
        Returns:
            (문서, 점수) 튜플 리스트
        """
        try:
            if self.vector_store is None:
                logger.warning("벡터 저장소가 초기화되지 않았습니다.")
                return []
            
            if self.store_type == "faiss":
                return self.vector_store.similarity_search_with_score(query, k=k)
            elif self.store_type == "chroma":
                return self.vector_store.similarity_search_with_score(
                    query, 
                    k=k,
                    filter=filter_dict
                )
            else:
                raise ValueError(f"지원하지 않는 저장소 타입: {self.store_type}")
                
        except Exception as e:
            logger.error(f"유사도 검색 실패: {e}")
            return []
    
    def save(self, path: Optional[str] = None) -> None:
        """
        벡터 저장소를 파일로 저장
        
        Args:
            path: 저장 경로 (None이면 기본 경로 사용)
        """
        try:
            if self.vector_store is None:
                logger.warning("저장할 벡터 저장소가 없습니다.")
                return
            
            if path is None:
                if self.store_type == "faiss":
                    path = Path(settings.vector_db_path) / "faiss_index"
                else:
                    path = Path(settings.chroma_db_path)
            
            if self.store_type == "faiss":
                self.vector_store.save_local(str(path))
            elif self.store_type == "chroma":
                self.vector_store.persist()
            
            logger.info(f"벡터 저장소가 저장되었습니다: {path}")
            
        except Exception as e:
            logger.error(f"벡터 저장소 저장 실패: {e}")
            raise
    
    def load(self, path: Optional[str] = None) -> None:
        """
        벡터 저장소를 파일에서 로드
        
        Args:
            path: 로드할 파일 경로 (None이면 기본 경로 사용)
        """
        try:
            if path is None:
                if self.store_type == "faiss":
                    path = Path(settings.vector_db_path) / "faiss_index"
                else:
                    path = Path(settings.chroma_db_path)
            
            if not Path(path).exists():
                logger.warning(f"벡터 저장소 파일이 존재하지 않습니다: {path}")
                return
            
            if self.store_type == "faiss":
                self.vector_store = FAISS.load_local(str(path), self.embeddings)
            elif self.store_type == "chroma":
                self.vector_store = Chroma(
                    persist_directory=str(path),
                    embedding_function=self.embeddings
                )
            
            logger.info(f"벡터 저장소가 로드되었습니다: {path}")
            
        except Exception as e:
            logger.error(f"벡터 저장소 로드 실패: {e}")
            raise
    
    def get_document_count(self) -> int:
        """저장된 문서 수 반환"""
        if self.vector_store is None:
            return 0
        
        if self.store_type == "faiss":
            return len(self.vector_store.index_to_docstore_id)
        elif self.store_type == "chroma":
            return self.vector_store._collection.count()
        
        return 0
    
    def clear(self) -> None:
        """벡터 저장소 초기화"""
        self.vector_store = None
        self.documents = []
        logger.info("벡터 저장소가 초기화되었습니다.")
    
    def get_statistics(self) -> Dict[str, Any]:
        """벡터 저장소 통계 정보 반환"""
        return {
            "store_type": self.store_type,
            "document_count": self.get_document_count(),
            "embedding_model": str(self.embeddings),
            "is_loaded": self.vector_store is not None
        }
