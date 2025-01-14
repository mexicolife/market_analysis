# Market Analysis System

A comprehensive system for analyzing real estate market data using Python and SQL, with integrated AI capabilities through Claude API.

## Features

- Advanced market analytics and trend analysis
- Integration with Claude AI for property analysis
- Automated data import and processing
- Interactive reporting system
- Property comparison tools
- Market prediction models

## Project Structure

```
market_analysis/
├── config/           # Configuration files
├── data/            # Data storage
├── notebooks/       # Jupyter notebooks for analysis
├── output/          # Generated reports and outputs
├── scripts/         # Python scripts
│   ├── advanced_analytics.py
│   ├── claude_api.py
│   ├── import_data.py
│   └── ...
└── requirements.txt
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/mexicolife/market_analysis.git
cd market_analysis
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your Anthropic API key and database credentials

5. Initialize the database:
```bash
python scripts/setup_database.py
```

## Usage

1. Import MLS data:
```bash
python scripts/import_data.py
```

2. Run market analysis:
```bash
python scripts/advanced_analytics.py
```

3. Use Claude for property analysis:
```bash
python scripts/claude_chat_gui.py
```

Refer to `USER_GUIDE.md` for detailed usage instructions.

## Development

- Follow the guidelines in `CODE_PRACTICES.md`
- Use virtual environment
- Run tests before committing changes

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details
