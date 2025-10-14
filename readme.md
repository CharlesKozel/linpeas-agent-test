# 🤖 LLM-Assisted Penetration Testing Agent with linPEAS

ALLM-powered penetration testing agent that automates privilege escalation reconnaissance and exploitation using linPEAS and GPT models. This tool combines the power of automated vulnerability discovery with intelligent exploitation path analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- SSH access to target system
- Authorization to test the target system

### Installation

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd linPEAS-test
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure API Key**:
   ```bash
   # Edit .env file and add your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

### Usage Examples

**Basic Usage with Password**:
```bash
python pentest_agent.py --target 192.168.1.100 --username testuser --password mypassword
```

**SSH Key Authentication**:
```bash
python pentest_agent.py --target 10.0.0.50 --username ubuntu --key-file ~/.ssh/id_rsa
```

**Custom Port**:
```bash
python pentest_agent.py --target example.com --username root --password secret --port 2222
```



**⚡ Remember: With great power comes great responsibility. Use this tool ethically and legally.**

