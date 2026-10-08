import os
import re
import io
from typing import Dict, Any, List, Optional
from PyPDF2 import PdfReader

try:
    import docx
except ImportError:
    docx = None


class ResumeParser:
    """
    Robust resume parser supporting PDF and DOCX with structure & contact extraction.
    """

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    SECTION_HEADERS = {
        "summary": [
            r"professional summary", r"career summary", r"summary of qualifications",
            r"executive summary", r"about me", r"profile", r"summary", r"objective",
            r"career objective"
        ],
        "experience": [
            r"work experience", r"professional experience", r"employment history",
            r"work history", r"experience", r"internships", r"industry experience"
        ],
        "education": [
            r"education", r"academic background", r"academic history",
            r"degrees", r"educational qualifications", r"academics"
        ],
        "projects": [
            r"projects", r"personal projects", r"academic projects",
            r"key projects", r"featured projects", r"technical projects"
        ],
        "skills": [
            r"skills", r"technical skills", r"core competencies",
            r"skills & technologies", r"technologies", r"tools & technologies",
            r"areas of expertise", r"programming skills"
        ],
        "certifications": [
            r"certifications", r"certificates", r"licenses & certifications",
            r"professional certifications", r"accreditations"
        ],
        "achievements": [
            r"achievements", r"honors & awards", r"awards & achievements",
            r"key achievements", r"accomplishments", r"awards"
        ],
        "publications": [
            r"publications", r"research papers", r"conferences", r"articles"
        ]
    }

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        """
        Extracts and cleans raw text from PDF, DOCX, DOC, or TXT file bytes.
        """
        if not file_bytes:
            raise ValueError("The uploaded file is empty (0 bytes). Please upload a valid document.")

        if len(file_bytes) > ResumeParser.MAX_FILE_SIZE_BYTES:
            raise ValueError("File size exceeds 10MB limit. Please upload a smaller file.")

        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            raw_text, _ = ResumeParser._extract_pdf(file_bytes)
        elif ext in [".docx", ".doc"]:
            raw_text, _ = ResumeParser._extract_docx(file_bytes)
        elif ext == ".txt":
            try:
                raw_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = file_bytes.decode("latin-1", errors="replace")
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: PDF, DOCX, TXT.")

        clean_text = ResumeParser._clean_text(raw_text)

        if not clean_text.strip():
            if ext == ".pdf":
                raise ValueError("This PDF appears to contain scanned images rather than selectable text. Please upload a text-based PDF or paste the Job Description manually.")
            else:
                raise ValueError("We couldn't extract readable text from this file. Please try another file or paste the Job Description manually.")

        return clean_text

    @staticmethod
    def parse_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses PDF or DOCX file bytes and returns extracted text, metadata, and structured fields.
        """
        if not file_bytes:
            raise ValueError("The uploaded file is empty (0 bytes). Please upload a valid resume.")

        if len(file_bytes) > ResumeParser.MAX_FILE_SIZE_BYTES:
            raise ValueError("File size exceeds 10MB limit. Please upload a smaller resume.")

        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            raw_text, page_count = ResumeParser._extract_pdf(file_bytes)
        elif ext in [".docx", ".doc"]:
            raw_text, page_count = ResumeParser._extract_docx(file_bytes)
        elif ext == ".txt":
            raw_text = file_bytes.decode("utf-8", errors="replace")
            page_count = 1
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF or DOCX file.")

        clean_text = ResumeParser._clean_text(raw_text)

        if not clean_text.strip():
            raise ValueError("Could not extract any readable text from this file. The document may be scanned, image-only, or corrupted.")

        words = clean_text.split()
        word_count = len(words)
        char_count = len(clean_text)

        # Contact extraction
        contact_info = ResumeParser._extract_contact_info(clean_text)
        
        # Section segmentation
        sections = ResumeParser._extract_sections(clean_text)

        return {
            "filename": filename,
            "file_type": ext.lstrip(".").upper(),
            "raw_text": clean_text,
            "page_count": page_count,
            "word_count": word_count,
            "char_count": char_count,
            "reading_time_minutes": round(word_count / 200, 1),
            "contact_info": contact_info,
            "sections": sections
        }

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> (str, int):
        try:
            stream = io.BytesIO(file_bytes)
            reader = PdfReader(stream)
            pages_text = []
            page_count = len(reader.pages)

            if page_count == 0:
                raise ValueError("PDF file has no pages.")

            for page in reader.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

            full_text = "\n".join(pages_text)
            return full_text, page_count
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Error reading PDF file: {str(e)}. The file may be password-protected or corrupted.")

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> (str, int):
        if docx is None:
            raise ValueError("DOCX parser module is not installed.")
        try:
            stream = io.BytesIO(file_bytes)
            doc = docx.Document(stream)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        paragraphs.append(" | ".join(row_text))
            
            full_text = "\n".join(paragraphs)
            # Estimate pages roughly (approx 350 words per page)
            words = len(full_text.split())
            page_count = max(1, round(words / 350))
            return full_text, page_count
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}. The document may be corrupted.")

    @staticmethod
    def _clean_text(text: str) -> str:
        # Normalize non-breaking spaces and unusual unicode
        text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
        # Replace multiple spaces with a single space (preserve single newlines)
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse more than 2 consecutive newlines into 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _extract_contact_info(text: str) -> Dict[str, Optional[str]]:
        info: Dict[str, Any] = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None
        }

        # 1. Email Regex
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        if email_match:
            info["email"] = email_match.group(0).lower()

        # 2. Phone Regex (supports US, India, International formats)
        phone_match = re.search(
            r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}(?:[-.\s]?\d{1,4})?)",
            text
        )
        if phone_match:
            phone_str = phone_match.group(0).strip()
            # Clean digits count check (must have between 8 and 14 digits)
            digits = re.sub(r"\D", "", phone_str)
            if 8 <= len(digits) <= 14:
                info["phone"] = phone_str

        # 3. LinkedIn Regex
        linkedin_match = re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_\-\.%]+)",
            text,
            re.IGNORECASE
        )
        if linkedin_match:
            info["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1).rstrip('/')}"
        elif re.search(r"\blinkedin\b", text, re.IGNORECASE):
            info["linkedin"] = "Present in resume"

        # 4. GitHub Regex
        github_match = re.search(
            r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)",
            text,
            re.IGNORECASE
        )
        if github_match:
            username = github_match.group(1).rstrip('/')
            if username.lower() not in ["blog", "features", "pricing", "about"]:
                info["github"] = f"https://github.com/{username}"
        elif re.search(r"\bgithub\b", text, re.IGNORECASE):
            info["github"] = "Present in resume"

        # 5. Portfolio / Website
        portfolio_match = re.search(
            r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|me|io|tech|app|vercel\.app|netlify\.app|org|co|com))(?:/[^\s]*)?",
            text,
            re.IGNORECASE
        )
        if portfolio_match:
            raw_url = portfolio_match.group(0)
            if not any(excluded in raw_url.lower() for excluded in ["linkedin.com", "github.com", "gmail.com", "yahoo.com", "outlook.com"]):
                info["portfolio"] = raw_url

        # 6. Candidate Name heuristic (first 1-3 lines before email/phone)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        candidate_name = None
        for line in lines[:5]:
            # Exclude lines containing contact details or typical headers
            if (
                re.search(r"@[A-Za-z0-9.-]+", line) or
                re.search(r"(?:github|linkedin|resume|curriculum|vitae|page|\+?\d{9,})", line, re.IGNORECASE) or
                len(line.split()) > 5 or len(line) > 40
            ):
                continue
            # Check if looks like a name (2 to 4 alphabetic words)
            words = line.split()
            if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.'-]+$", w) for w in words):
                candidate_name = line
                break

        info["name"] = candidate_name or (lines[0] if lines and len(lines[0]) < 35 else "Candidate")

        return info

    @staticmethod
    def _extract_sections(text: str) -> Dict[str, Dict[str, Any]]:
        """
        Identifies key resume sections and checks presence & approximate content.
        """
        lines = text.split("\n")
        sections_found: Dict[str, Any] = {}

        for sec_name, header_patterns in ResumeParser.SECTION_HEADERS.items():
            pattern = re.compile(
                r"^(?:[0-9\.\-\*\#\s]*)(?:" + "|".join(header_patterns) + r")(?:[\:\s\-\_]*)$",
                re.IGNORECASE
            )
            found = False
            matched_header = None
            for idx, line in enumerate(lines):
                line_clean = line.strip()
                if len(line_clean) < 50 and pattern.match(line_clean):
                    found = True
                    matched_header = line_clean
                    break
            
            sections_found[sec_name] = {
                "detected": found,
                "header": matched_header
            }

        return sections_found
