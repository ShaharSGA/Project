# 🧠 Dana's Brain - AI Marketing Content Generator

<div align="center">

**Autonomous AI system for generating personalized Hebrew marketing content**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange.svg)](https://www.crewai.com/)
[![Chainlit](https://img.shields.io/badge/Chainlit-UI-green.svg)](https://chainlit.io/)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB-red.svg)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

**Dana's Brain** is an advanced AI system that generates professional Hebrew marketing content using RAG (Retrieval-Augmented Generation) and Multi-Agent Architecture.

The system mimics Dana's unique writing style (Marketing Manager at Lierac Israel) and generates platform-specific content for LinkedIn, Facebook, and Instagram.

### 🎯 Key Features

- 🤖 **2 Autonomous AI Agents** working in sequence
- 📚 **RAG-powered knowledge retrieval** with ChromaDB
- 📱 **9 ready-to-publish posts** (3 per platform)
- 🎨 **Interactive Chainlit UI** with dynamic forms
- 💾 **Auto-save** to Markdown files with timestamps
- ✨ **4 writing personas** to match different brand voices

---

## 🔄 How It Works

```
1. User Input
   ↓
2. Strategy Architect Agent
   → Searches methodology knowledge base (RAG)
   → Creates strategic brief in Hebrew
   ↓
3. Dana Copywriter Agent
   → Searches voice examples & style guide (RAG)
   → Writes 9 platform-optimized posts
   ↓
4. Output
   → Saved to Markdown file
   → Displayed in UI
```

### The Agents

**🎯 Strategy Architect**
- Analyzes product data
- Searches Dana's methodology via RAG
- Creates comprehensive strategic brief
- Defines hooks, storytelling angles, and platform strategies

**✍️ Dana Copywriter**
- Receives strategic brief as context
- Searches voice examples and style guide via RAG
- Writes content matching Dana's authentic voice
- Generates 3 posts per platform (Emotional, Expert, Sales)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | CrewAI (Multi-Agent Orchestration) |
| **UI** | Chainlit (Interactive Web Interface) |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector DB** | ChromaDB |
| **RAG Tools** | TXTSearchTool from crewai-tools |
| **Language** | Python 3.10+ |

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API key
- Git

### Setup Steps

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/AI_Final_151225.git
cd AI_Final_151225
```

**2. Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

**5. Run the application**
```bash
chainlit run start.py
```

The interface will open at `http://localhost:8000`

---

## 🚀 Usage

### Step 1: Fill the Form
- **Product Name** - Name of the product/service
- **Key Benefits** - Main advantages
- **Target Audience** - Who is this for?
- **The Offer** - Discount, promotion, or special offer
- **Persona** - Choose Dana's writing style:
  - Professional Dana
  - Friendly Dana
  - Inspirational Dana
  - Mentor Dana

### Step 2: Submit
Send any message (e.g., "Let's start") to activate the agents.

### Step 3: Wait
The system takes 2-3 minutes to:
- Search knowledge bases
- Create strategic brief
- Generate 9 posts

### Step 4: Review & Use
- View output in the interface
- Find saved file in `outputs/` folder
- Copy posts to social media platforms

---

## 📁 Project Structure

```
AI_Final_151225/
├── agents/                          # AI Agent definitions
│   ├── strategy_architect.py        # Strategy agent
│   └── dana_copywriter.py           # Copywriter agent
├── tasks/                           # Agent tasks
│   ├── strategy_tasks.py            # Strategy task definition
│   └── copywriting_tasks.py         # Copywriting task definition
├── tools/                           # RAG tools
│   └── txt_search_tools.py          # TXTSearchTool with ChromaDB
├── Data/                            # Knowledge base documents
│   ├── Dana_Brain_Methodology.txt   # Marketing methodology
│   ├── Dana_Voice_Examples_Lierac.txt  # Voice examples
│   └── style_guide_customer_Lierac.txt # Style guide
├── outputs/                         # Generated content
├── start.py                         # Main application entry
├── chainlit.md                      # Welcome message
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (create this)
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 📊 Output Examples

### Strategic Brief Structure
```
PART A: THE DEEP DIVE
- Product Philosophy
- Simplified Science
- Sensory Experience

PART B: STRATEGIC LENS
- The Gap
- Buying Barriers
- Psychological Trigger

PART C: CREATIVE TOOLKIT
- Hooks Bank
- Storytelling Angles
- Feature-to-Benefit Table
- Offer Framing

PART D: PLATFORM STRATEGY
- LinkedIn recommendations
- Facebook recommendations
- Instagram recommendations
```

### Post Format (LinkedIn Example)
```
Hey [greeting],

[Emotional hook or question]

[Personal story or insight]

[Value proposition]

[Call to action]

**CTA:** [Specific action]
**Hashtags:** #tag1 #tag2
```

---

## ⚙️ Configuration

### Change LLM Model

Edit `agents/strategy_architect.py`:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",  # Change to gpt-4, gpt-4-turbo, etc.
    temperature=0.5
)
```

### Change Embedding Model

Edit `tools/txt_search_tools.py`:
```python
EMBEDDING_CONFIG = {
    "provider": "openai",
    "config": {
        "model": "text-embedding-3-large",  # Upgrade for better accuracy
    }
}
```

### Adjust Verbosity

Edit `start.py`:
```python
crew = Crew(
    agents=[strategy_architect, dana_copywriter],
    tasks=[strategy_task, copywriting_task],
    process=Process.sequential,
    verbose=True  # Set to False for less logging
)
```

---

## 🧪 Testing

Run a test campaign:

1. **Product:** "Anti-aging face mask - new edition"
2. **Benefits:** "Deep hydration, instant glow, natural ingredients"
3. **Audience:** "Women 35-50, interested in skincare"
4. **Offer:** "15% off + free shipping"
5. **Persona:** Professional Dana

Expected output: Strategic brief + 9 posts in ~2-3 minutes

---

## 🔍 RAG Implementation

The system uses **TXTSearchTool** for semantic search:

1. **Indexing Phase:**
   - Documents are split into chunks
   - Each chunk is embedded using OpenAI
   - Embeddings stored in ChromaDB

2. **Search Phase:**
   - Agent query is embedded
   - Similar chunks are retrieved
   - Relevant context is returned to agent

3. **Knowledge Base Files:**
   - `Dana_Brain_Methodology.txt` - Used by Strategy Architect
   - `Dana_Voice_Examples_Lierac.txt` - Used by Dana Copywriter
   - `style_guide_customer_Lierac.txt` - Used by Dana Copywriter

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Dana** - For the unique methodology and writing style
- **Lierac Israel** - For providing content examples
- **CrewAI Team** - For the excellent multi-agent framework
- **Chainlit Team** - For the beautiful UI framework
- **OpenAI** - For GPT and embedding models

---

## 👤 Author

**Shahar** - [GitHub Profile](https://github.com/YOUR_USERNAME)

---

## 📞 Support

If you encounter issues:
1. Check the `.env` file has correct API key
2. Ensure all dependencies are installed
3. Check `run.log` for error details
4. Open an issue on GitHub

---

<div align="center">

**Made with ❤️ and 🤖**

⭐ Star this repo if you find it useful!

[⬆ Back to Top](#-danas-brain---ai-marketing-content-generator)

</div>
