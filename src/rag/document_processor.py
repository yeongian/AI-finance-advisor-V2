"""
문서 처리 모듈
금융 관련 문서를 전처리하고 청킹하는 기능
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    CSVLoader,
    JSONLoader
)

from ..core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """문서 처리 및 청킹 클래스"""
    
    def __init__(self):
        """문서 프로세서 초기화"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 지원하는 파일 확장자
        self.supported_extensions = {
            '.txt': self._load_text,
            '.md': self._load_text,
            '.pdf': self._load_pdf,
            '.csv': self._load_csv,
            '.json': self._load_json
        }
    
    def process_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        파일을 처리하여 Document 리스트로 변환
        
        Args:
            file_path: 처리할 파일 경로
            metadata: 추가할 메타데이터
            
        Returns:
            처리된 Document 리스트
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"파일이 존재하지 않습니다: {file_path}")
                return []
            
            # 파일 확장자 확인
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                logger.warning(f"지원하지 않는 파일 형식: {extension}")
                return []
            
            # 파일 로드
            documents = self.supported_extensions[extension](file_path)
            
            # 메타데이터 추가
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
                    doc.metadata['source'] = str(file_path)
                    doc.metadata['file_type'] = extension
            
            # 청킹
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"파일 처리 완료: {file_path} -> {len(chunks)}개 청크")
            return chunks
            
        except Exception as e:
            logger.error(f"파일 처리 실패: {file_path}, 오류: {e}")
            return []
    
    def process_directory(self, directory_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        디렉토리 내 모든 지원 파일을 처리
        
        Args:
            directory_path: 처리할 디렉토리 경로
            metadata: 추가할 메타데이터
            
        Returns:
            처리된 Document 리스트
        """
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                logger.error(f"디렉토리가 존재하지 않습니다: {directory_path}")
                return []
            
            all_documents = []
            
            # 지원하는 확장자를 가진 파일들 찾기
            for extension in self.supported_extensions.keys():
                files = list(directory.glob(f"**/*{extension}"))
                
                for file_path in files:
                    documents = self.process_file(str(file_path), metadata)
                    all_documents.extend(documents)
            
            logger.info(f"디렉토리 처리 완료: {directory_path} -> {len(all_documents)}개 청크")
            return all_documents
            
        except Exception as e:
            logger.error(f"디렉토리 처리 실패: {directory_path}, 오류: {e}")
            return []
    
    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        텍스트를 직접 처리하여 Document 리스트로 변환
        
        Args:
            text: 처리할 텍스트
            metadata: 추가할 메타데이터
            
        Returns:
            처리된 Document 리스트
        """
        try:
            # 텍스트 정리
            cleaned_text = self._clean_text(text)
            
            # Document 생성
            document = Document(
                page_content=cleaned_text,
                metadata=metadata or {}
            )
            
            # 청킹
            chunks = self.text_splitter.split_documents([document])
            
            logger.info(f"텍스트 처리 완료: {len(cleaned_text)}자 -> {len(chunks)}개 청크")
            return chunks
            
        except Exception as e:
            logger.error(f"텍스트 처리 실패: {e}")
            return []
    
    def _load_text(self, file_path: Path) -> List[Document]:
        """텍스트 파일 로드"""
        try:
            loader = TextLoader(str(file_path), encoding='utf-8')
            return loader.load()
        except Exception as e:
            logger.error(f"텍스트 파일 로드 실패: {file_path}, 오류: {e}")
            return []
    
    def _load_pdf(self, file_path: Path) -> List[Document]:
        """PDF 파일 로드"""
        try:
            loader = PDFMinerLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"PDF 파일 로드 실패: {file_path}, 오류: {e}")
            return []
    
    def _load_csv(self, file_path: Path) -> List[Document]:
        """CSV 파일 로드"""
        try:
            loader = CSVLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"CSV 파일 로드 실패: {file_path}, 오류: {e}")
            return []
    
    def _load_json(self, file_path: Path) -> List[Document]:
        """JSON 파일 로드"""
        try:
            loader = JSONLoader(
                file_path=str(file_path),
                jq_schema='.[]',
                text_content=False
            )
            return loader.load()
        except Exception as e:
            logger.error(f"JSON 파일 로드 실패: {file_path}, 오류: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 특수 문자 정리 (금융 관련 특수 문자는 유지)
        text = re.sub(r'[^\w\s\-.,!?()%$₩€¥£]', '', text)
        
        # 연속된 줄바꿈 제거
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    def create_financial_knowledge_base(self) -> List[Document]:
        """기본 금융 지식베이스 생성"""
        financial_documents = [
            {
                "content": """
                개인 재무 관리의 기본 원칙

                1. 수입과 지출 관리
                - 수입을 먼저 파악하고 지출을 계획하세요
                - 50/30/20 법칙: 수입의 50%는 필수지출, 30%는 선택지출, 20%는 저축/투자
                - 월별 예산을 세우고 지출을 추적하세요

                2. 비상금 확보
                - 3-6개월치 생활비를 비상금으로 준비하세요
                - 비상금은 안전하고 유동성이 높은 곳에 보관하세요
                - 정기적으로 비상금을 점검하고 보충하세요

                3. 부채 관리
                - 고금리 부채부터 우선적으로 상환하세요
                - 신용카드 사용을 제한하고 현금 사용을 늘리세요
                - 부채 상환 계획을 세우고 지키세요
                """,
                "metadata": {
                    "category": "personal_finance",
                    "topic": "basic_principles",
                    "title": "개인 재무 관리 기본 원칙"
                }
            },
            {
                "content": """
                투자 포트폴리오 구성 전략

                1. 자산 배분
                - 나이와 위험 성향에 따라 자산을 배분하세요
                - 100 - 나이 = 주식 비중 (예: 30세면 70% 주식)
                - 나머지는 채권, 현금 등 안전자산으로 배분

                2. 분산 투자
                - 한 종목에 모든 돈을 투자하지 마세요
                - 업종, 지역, 자산군을 다양화하세요
                - 정기적으로 포트폴리오를 리밸런싱하세요

                3. 장기 투자
                - 단기 변동에 일희일비하지 마세요
                - 복리의 힘을 믿고 장기적으로 투자하세요
                - 정기적인 투자(달러 코스트 애버리징)를 활용하세요
                """,
                "metadata": {
                    "category": "investment",
                    "topic": "portfolio_strategy",
                    "title": "투자 포트폴리오 구성 전략"
                }
            },
            {
                "content": """
                세금 절약 전략

                1. 연말정산 최적화
                - 의료비, 교육비, 기부금 등 공제 항목을 최대한 활용하세요
                - 신용카드 사용 내역을 정리하여 소득공제를 받으세요
                - 투자 손실을 활용하여 세금을 절약하세요

                2. 투자 관련 세금
                - 장기 투자 시 양도소득세 혜택을 받을 수 있습니다
                - ISA(개인종합자산계좌)를 활용하여 세금 혜택을 받으세요
                - 연금저축, IRP 등을 활용하여 세금 공제를 받으세요

                3. 사업자 세금
                - 사업자라면 필요경비를 정확히 기록하세요
                - 부가가치세 신고를 정확히 하여 환급받으세요
                - 세무사와 상담하여 최적의 세금 전략을 수립하세요
                """,
                "metadata": {
                    "category": "tax",
                    "topic": "tax_saving",
                    "title": "세금 절약 전략"
                }
            },
            {
                "content": """
                부동산 투자 가이드

                1. 투자 전 준비사항
                - 시장 조사: 해당 지역의 시세, 수요, 공급을 파악하세요
                - 재정 계획: 구매 자금, 유지비용, 수익률을 계산하세요
                - 리스크 관리: 시장 변동, 임차인 관리 등 위험 요소를 고려하세요

                2. 수익률 계산
                - 월세 수익률 = (월세 - 관리비) / 투자금액 × 12 × 100
                - 전세 수익률 = (전세금 - 투자금액) / 투자금액 × 100
                - 매매 수익률 = (매도가 - 매수가) / 매수가 × 100

                3. 투자 전략
                - 위치가 중요합니다: 교통, 편의시설, 교육환경을 고려하세요
                - 건물 상태를 점검하고 리모델링 비용을 고려하세요
                - 임대 관리 업무를 고려하여 시간과 노력을 계산하세요
                """,
                "metadata": {
                    "category": "real_estate",
                    "topic": "investment_guide",
                    "title": "부동산 투자 가이드"
                }
            },
            {
                "content": """
                은퇴 계획 수립

                1. 은퇴 자금 계산
                - 은퇴 후 필요 생활비를 계산하세요 (현재 생활비의 70-80%)
                - 은퇴 시점까지의 기간을 고려하여 목표 금액을 설정하세요
                - 인플레이션을 고려하여 실질 구매력을 유지하세요

                2. 은퇴 준비 방법
                - 국민연금, 직장연금 등 공적 연금을 최대한 활용하세요
                - 개인연금, IRP 등을 통해 추가 연금을 준비하세요
                - 부동산, 주식 등 다양한 자산을 통해 수익을 창출하세요

                3. 은퇴 후 관리
                - 은퇴 후에도 일정 수준의 수입을 유지하는 방법을 고려하세요
                - 건강 관리와 취미 활동을 통해 삶의 질을 유지하세요
                - 자녀와의 관계, 사회적 관계를 유지하세요
                """,
                "metadata": {
                    "category": "retirement",
                    "topic": "planning",
                    "title": "은퇴 계획 수립"
                }
            }
        ]
        
        documents = []
        for doc in financial_documents:
            document = Document(
                page_content=doc["content"],
                metadata=doc["metadata"]
            )
            documents.append(document)
        
        # 청킹
        chunks = self.text_splitter.split_documents(documents)
        
        logger.info(f"금융 지식베이스 생성 완료: {len(chunks)}개 청크")
        return chunks
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """처리 통계 정보 반환"""
        return {
            "supported_extensions": list(self.supported_extensions.keys()),
            "chunk_size": settings.rag_chunk_size,
            "chunk_overlap": settings.rag_chunk_overlap,
            "text_splitter_type": type(self.text_splitter).__name__
        }
