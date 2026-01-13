import pytest
from unittest.mock import MagicMock, patch
from src.clinvar import get_pubmed_abstracts

@pytest.mark.asyncio
async def test_get_pubmed_abstracts_parsing():
    # Mock XML response with structured abstract
    mock_xml = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article>
                    <ArticleTitle>Test Title</ArticleTitle>
                    <Journal>
                        <Title>Test Journal</Title>
                        <JournalIssue>
                            <PubDate>
                                <Year>2023</Year>
                                <Month>Jan</Month>
                            </PubDate>
                        </JournalIssue>
                    </Journal>
                    <Abstract>
                        <AbstractText Label="BACKGROUND">Background info.</AbstractText>
                        <AbstractText Label="RESULTS">Results info.</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    
    # Mock XML response with simple string abstract
    mock_xml_simple = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>67890</PMID>
                <Article>
                    <ArticleTitle>Simple Title</ArticleTitle>
                    <Journal>
                        <Title>Simple Journal</Title>
                        <JournalIssue>
                            <PubDate>
                                <Year>2022</Year>
                            </PubDate>
                        </JournalIssue>
                    </Journal>
                    <Abstract>
                        <AbstractText>Just a simple abstract paragraph.</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    
    # Test Structured
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_xml
        mock_get.return_value = mock_response
        
        results = await get_pubmed_abstracts(["12345"])
        
        assert len(results) == 1
        assert results[0]["id"] == "12345"
        assert "Background info" in results[0]["abstract"]
        assert "BACKGROUND:" in results[0]["abstract"] # Check format
        assert results[0]["pubdate"] == "2023 Jan"

    # Test Simple
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_xml_simple
        mock_get.return_value = mock_response
        
        results = await get_pubmed_abstracts(["67890"])
        
        assert len(results) == 1
        assert results[0]["id"] == "67890"
        assert "Just a simple abstract paragraph" in results[0]["abstract"]
