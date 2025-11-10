# src.crawlers.base_crawler

Base Crawler Class for CORTEX

Provides abstract base class and common infrastructure for all CORTEX crawlers.
All crawlers (UI, API, Database, etc.) inherit from BaseCrawler.

Architecture:
- Standardized lifecycle (initialize → validate → crawl → store → cleanup)
- Error handling and retry logic
- Progress reporting
- Result standardization
- Knowledge graph integration

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
