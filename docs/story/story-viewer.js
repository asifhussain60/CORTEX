/**
 * CORTEX Story Viewer - Interactive Chapter Navigation
 * Author: Asif Hussain
 * Copyright © 2025 Asif Hussain. All rights reserved.
 */

// Chapter Configuration with Images
const CHAPTERS = {
    'prologue': {
        id: 'prologue',
        number: 'PROLOGUE',
        title: 'The Basement Laboratory',
        file: 'Prologue/PROLOGUE.txt',
        meta: ['🏗️ Setup', '~2,000 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-prologue-01.jpeg', position: 'right' },
            { src: 'illustrations/images/essentials/cortex-awakening-prologue-02.jpeg', position: 'left' }
        ],
        next: 'chapter-01',
        prev: null
    },
    'chapter-01': {
        id: 'chapter-01',
        number: 'CHAPTER 1',
        title: 'The Amnesia Crisis',
        file: 'Chapter-01/CHAPTER-01.txt',
        meta: ['Problem Statement', '~1,800 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch01-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch01-02.jpeg', position: 'right' },
            { src: 'illustrations/images/essentials/cortex-awakening-ch01-03.jpeg', position: 'left' }
        ],
        next: 'chapter-02',
        prev: 'prologue'
    },
    'chapter-02': {
        id: 'chapter-02',
        number: 'CHAPTER 2',
        title: 'Tier 0 - The Gatekeeper',
        file: 'Chapter-02/CHAPTER-02.txt',
        meta: ['🛡️ Brain Protector + SKULL', '~2,500 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch02-01.jpeg', position: 'right' },
            { src: 'illustrations/images/essentials/cortex-awakening-ch02-02.jpeg', position: 'left' }
        ],
        next: 'chapter-03',
        prev: 'chapter-01'
    },
    'chapter-03': {
        id: 'chapter-03',
        number: 'CHAPTER 3',
        title: 'Tier 1 - Memory Awakens',
        file: 'Chapter-03/CHAPTER-03.txt',
        meta: ['💾 Working Memory (Tier 1)', '~2,200 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch03-01.jpeg', position: 'left' }
        ],
        next: 'chapter-04',
        prev: 'chapter-02'
    },
    'chapter-04': {
        id: 'chapter-04',
        number: 'CHAPTER 4',
        title: 'Tier 2 - The Learning Machine',
        file: 'Chapter-04/CHAPTER-04.txt',
        meta: ['🧬 Knowledge Graph (Tier 2)', '~2,300 words'],
        images: [],
        next: 'chapter-05',
        prev: 'chapter-03'
    },
    'chapter-05': {
        id: 'chapter-05',
        number: 'CHAPTER 5',
        title: 'The Test-Driven Rebellion',
        file: 'Chapter-05/CHAPTER-05.txt',
        meta: ['✅ TDD Mastery', '~2,400 words'],
        images: [
            { src: 'illustrations/images/valuable/cortex-awakening-ch05-01.jpeg', position: 'right' }
        ],
        next: 'chapter-06',
        prev: 'chapter-04'
    },
    'chapter-06': {
        id: 'chapter-06',
        number: 'CHAPTER 6',
        title: 'The Great Orchestration',
        file: 'Chapter-06/CHAPTER-06.txt',
        meta: ['🎼 Base/Execution Orchestrators', '~2,500 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch06-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch06-02.jpeg', position: 'right' }
        ],
        next: 'chapter-07',
        prev: 'chapter-05'
    },
    'chapter-07': {
        id: 'chapter-07',
        number: 'CHAPTER 7',
        title: 'The Planning Revolution',
        file: 'Chapter-07/CHAPTER-07.txt',
        meta: ['📋 Planning System', '~2,600 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch07-01.jpeg', position: 'right' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch07-02.jpeg', position: 'left' }
        ],
        next: 'chapter-08',
        prev: 'chapter-06'
    },
    'chapter-08': {
        id: 'chapter-08',
        number: 'CHAPTER 8',
        title: 'The Enterprise Awakening',
        file: 'Chapter-08/CHAPTER-08.txt',
        meta: ['🏢 ADO Operations', '~2,200 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch08-01.jpeg', position: 'left' }
        ],
        next: 'chapter-09',
        prev: 'chapter-07'
    },
    'chapter-09': {
        id: 'chapter-09',
        number: 'CHAPTER 9',
        title: 'The Sanitizer\'s Dilemma',
        file: 'Chapter-09/CHAPTER-09.txt',
        meta: ['🧹 Code Sanitization', '~2,300 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch09-01.jpeg', position: 'right' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch09-02.jpeg', position: 'left' }
        ],
        next: 'chapter-10',
        prev: 'chapter-08'
    },
    'chapter-10': {
        id: 'chapter-10',
        number: 'CHAPTER 10',
        title: 'The Self-Healing System',
        file: 'Chapter-10/CHAPTER-10.txt',
        meta: ['🔧 System Maintenance', '~2,400 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch10-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch10-02.jpeg', position: 'right' }
        ],
        next: 'chapter-11',
        prev: 'chapter-09'
    },
    'chapter-11': {
        id: 'chapter-11',
        number: 'CHAPTER 11',
        title: 'The Knowledge Keeper',
        file: 'Chapter-11/CHAPTER-11.txt',
        meta: ['📚 Knowledge Library (Tier 3)', '~2,200 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch11-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch11-02.jpeg', position: 'right' }
        ],
        next: 'chapter-12',
        prev: 'chapter-10'
    },
    'chapter-12': {
        id: 'chapter-12',
        number: 'CHAPTER 12',
        title: 'The Convergence',
        file: 'Chapter-12/CHAPTER-12.txt',
        meta: ['🌐 Multi-Repo + Refinement', '~2,800 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-epilogue-01.jpeg', position: 'right' }
        ],
        next: 'chapter-13',
        prev: 'chapter-11'
    },
    'chapter-13': {
        id: 'chapter-13',
        number: 'CHAPTER 13',
        title: 'The Refiner',
        file: 'Chapter-13/CHAPTER-13.txt',
        meta: ['✨ System Refinement', '~2,500 words'],
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch13-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch13-02.jpeg', position: 'right' }
        ],
        next: null,
        prev: 'chapter-12'
    }
};

// Current chapter state
let currentChapter = null;

/**
 * Initialize the story viewer
 */
function init() {
    // Check URL hash for chapter, default to prologue
    const hash = window.location.hash.slice(1) || 'prologue';
    
    // Setup navigation listeners first
    setupNavigation();
    
    // Load initial chapter
    loadChapter(hash);

    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
        const newHash = window.location.hash.slice(1) || 'prologue';
        loadChapter(newHash);
    });
}

/**
 * Setup navigation event listeners
 */
function setupNavigation() {
    const chapterLinks = document.querySelectorAll('.chapter-link');
    chapterLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const chapterId = link.dataset.chapter;
            window.location.hash = chapterId;
            loadChapter(chapterId);
            
            // Update active state
            chapterLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

/**
 * Load a chapter
 */
async function loadChapter(chapterId) {
    const chapter = CHAPTERS[chapterId];
    if (!chapter) {
        console.error('Chapter not found:', chapterId);
        showError('Chapter not found');
        return;
    }

    currentChapter = chapterId;
    showLoading();

    try {
        // Fetch chapter content - use relative path from viewer.html location
        const response = await fetch(chapter.file);
        if (!response.ok) {
            throw new Error(`Failed to load chapter: ${response.status} ${response.statusText}`);
        }
        
        const content = await response.text();
        renderChapter(chapter, content);
        
        // Update active state in sidebar
        updateSidebarActive(chapterId);
    } catch (error) {
        console.error('Error loading chapter:', error);
        showError(`Failed to load chapter: ${error.message}. Please try again.`);
    }
}

/**
 * Render chapter content
 */
function renderChapter(chapter, content) {
    const container = document.getElementById('chapterContent');
    
    // Parse content with embedded images
    const html = parseChapterContent(content, chapter.images || []);
    
    // Build chapter HTML
    const chapterHTML = `
        <div class="chapter-container">
            <div class="chapter-header">
                <div class="chapter-meta">
                    ${chapter.meta.map(m => `<span class="meta-badge">${m}</span>`).join('')}
                </div>
                <h1>${chapter.number}: ${chapter.title}</h1>
            </div>
            
            <div class="chapter-body">
                ${html}
            </div>
            
            <div class="chapter-navigation">
                ${renderPrevButton(chapter)}
                ${renderNextButton(chapter)}
            </div>
        </div>
    `;
    
    container.innerHTML = chapterHTML;
    
    // Setup navigation button listeners
    setupChapterNavButtons();
}

/**
 * Parse chapter content from text to HTML with embedded images
 * Uses section-aware distribution to ensure contextual placement
 */
function parseChapterContent(text, images) {
    // Remove first line (chapter title - already in header)
    const lines = text.split('\n').slice(1);
    
    // First pass: Count sections to calculate optimal image placement
    const sections = [];
    let currentSection = { startLine: 0, paragraphCount: 0 };
    
    lines.forEach((line, index) => {
        line = line.trim();
        if (line.startsWith('## ')) {
            if (currentSection.paragraphCount > 0) {
                sections.push(currentSection);
            }
            currentSection = { startLine: index, paragraphCount: 0, title: line.slice(3) };
        } else if (line && !line.startsWith('###') && !line.startsWith('---')) {
            currentSection.paragraphCount++;
        }
    });
    if (currentSection.paragraphCount > 0) {
        sections.push(currentSection);
    }
    
    // Calculate image placement points (distribute evenly with minimum 2-section gap)
    const imagePlacement = calculateImagePlacement(sections.length, images.length);
    
    // Second pass: Render HTML with contextual image placement and character dialog colors
    let html = '';
    let inParagraph = false;
    let sectionIndex = -1;
    let paragraphsInSection = 0;
    let imageIndex = 0;
    let paragraphBuffer = ''; // Buffer to collect full paragraph before processing
    
    for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        let line = lines[lineIndex].trim();
        
        // Empty line
        if (!line) {
            if (inParagraph) {
                // Process buffered paragraph with character dialog detection
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            continue;
        }
        
        // Heading level 2 (##) - New section
        if (line.startsWith('## ')) {
            if (inParagraph) {
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            
            sectionIndex++;
            paragraphsInSection = 0;
            html += `<h2>${line.slice(3)}</h2>`;
            continue;
        }
        
        // Heading level 3 (###)
        if (line.startsWith('### ')) {
            if (inParagraph) {
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            html += `<h3>${line.slice(4)}</h3>`;
            continue;
        }
        
        // Horizontal rule
        if (line === '---') {
            if (inParagraph) {
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            html += '<hr style="border: none; border-top: 1px solid var(--glass-border); margin: 2rem 0;">';
            continue;
        }
        
        // Regular paragraph
        if (!inParagraph) {
            html += '<p>';
            inParagraph = true;
        }
        
        // Process inline formatting
        line = processInlineFormatting(line);
        paragraphBuffer += line + ' ';
        
        // Check if we should place an image after this paragraph
        // Place image after 2nd paragraph in designated sections for contextual relevance
        if (inParagraph && paragraphsInSection === 1 && 
            imageIndex < images.length && 
            imagePlacement.includes(sectionIndex)) {
            html += processCharacterDialog(paragraphBuffer) + '</p>';
            paragraphBuffer = '';
            inParagraph = false;
            html += createInlineImage(images[imageIndex]);
            imageIndex++;
        }
        
        paragraphsInSection++;
    }
    
    if (inParagraph) {
        html += processCharacterDialog(paragraphBuffer) + '</p>';
    }
    
    return html;
}

/**
 * Process character dialog with consistent color coding
 * Detects character names and applies glassmorphism-compatible colors
 * IMPORTANT: Only changes color, NOT font-size (maintains 1.3em from Comic Sans)
 */
function processCharacterDialog(text) {
    // Character color palette (glassmorphism theme)
    const characterColors = {
        'Asif': '#00d4ff',           // Cyan - protagonist
        'Miss G': '#ba55d3',         // Medium orchid - supportive inner voice
        'Copilot': '#7b61ff',        // Purple - AI assistant
        'CORTEX': '#ff6b6b',         // Coral red - system voice
        'client': '#ffb347',         // Orange - external characters
        'Mom': '#ff69b4',            // Hot pink - family
        'he': '#00d4ff',             // Asif (pronoun)
        'He': '#00d4ff',             // Asif (pronoun)
        'she': '#ba55d3',            // Miss G (pronoun)
        'She': '#ba55d3'             // Miss G (pronoun)
    };
    
    // Process quoted dialog with character detection
    text = text.replace(/"([^"]+)"/g, (match, dialog, offset) => {
        // Get context before the quote (up to 150 chars for better detection)
        const contextBefore = text.substring(Math.max(0, offset - 150), offset);
        
        // Check which character is speaking based on context
        for (const [character, color] of Object.entries(characterColors)) {
            // Expanded pattern list to catch more dialog attribution styles
            const patterns = [
                // Direct attribution: "Asif asked"
                new RegExp(`${character}[^.]*?$`, 'i'),
                // Possessive: "Asif's voice"
                new RegExp(`${character}'s[^.]*?$`, 'i'),
                // Action verbs: "Asif asked/said/responded/etc"
                new RegExp(`${character} (?:asked|said|responded|replied|explained|observed|suggested|confirmed|gestured|pointed|looked up|turned|stopped|ran|squinted|spun back|finally|materialized)`, 'i'),
                // Pronouns with actions: "He said", "She asked"
                new RegExp(`${character} (?:didn't|did|stopped|turned|ran|gestured|pointed|looked|surveyed|studied|finally)`, 'i'),
                // Direct presence: "in his/her thoughts/mind/consciousness"
                new RegExp(`${character}[^.]{0,30}(?:thoughts|mind|consciousness|voice|presence)`, 'i')
            ];
            
            if (patterns.some(pattern => pattern.test(contextBefore))) {
                // Apply color with 10% reduction in font-size (1.17em = 90% of 1.3em)
                return `<span style="color: ${color}; font-weight: 500; text-shadow: 0 0 20px ${color}40; font-size: 0.9em;">"${dialog}"</span>`;
            }
        }
        
        // Default dialog style (neutral with slight glow) - 10% reduction
        return `<span style="color: #c8c8ff; font-weight: 500; font-size: 0.9em;">"${dialog}"</span>`;
    });
    
    return text;
}

/**
 * Calculate optimal section indices for image placement
 * Ensures even distribution, adapts to chapter length
 */
function calculateImagePlacement(totalSections, imageCount) {
    if (imageCount === 0 || totalSections === 0) return [];
    if (imageCount === 1) return [Math.floor(totalSections / 2)]; // Middle section
    
    const placement = [];
    
    // Adaptive gap: Use 1-section minimum for short chapters, 2 for longer ones
    const minGap = totalSections >= imageCount * 3 ? 2 : 1;
    
    // Check if we have enough sections for requested images
    if (totalSections < imageCount) {
        // If more images than sections, place one image per section
        for (let i = 0; i < Math.min(imageCount, totalSections); i++) {
            placement.push(i);
        }
        return placement;
    }
    
    // Calculate even distribution
    const step = Math.max(minGap + 1, Math.floor(totalSections / (imageCount + 1)));
    
    for (let i = 0; i < imageCount; i++) {
        const sectionIndex = Math.min(
            (i + 1) * step,
            totalSections - (imageCount - i - 1) * (minGap + 1) - 1
        );
        placement.push(sectionIndex);
    }
    
    return placement;
}

/**
 * Create inline image with text wrapping
 */
function createInlineImage(image) {
    const position = image.position || 'right';
    const floatStyle = position === 'right' ? 'float: right; margin: 0 0 1.5rem 2rem;' : 'float: left; margin: 0 2rem 1.5rem 0;';
    
    return `
        <div style="${floatStyle} max-width: 45%; min-width: 300px;">
            <img src="${image.src}" 
                 alt="Story illustration" 
                 style="width: 100%; border-radius: var(--radius-md); border: 1px solid var(--glass-border); box-shadow: var(--shadow);" />
        </div>
    `;
}

/**
 * Process inline formatting (bold, italic, etc.)
 */
function processInlineFormatting(text) {
    // Bold (**text**)
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Italic (*text*)
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Code (`code`)
    text = text.replace(/`(.+?)`/g, '<code style="background: rgba(0,212,255,0.1); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: var(--font-mono); font-size: 0.9em;">$1</code>');
    
    return text;
}

/**
 * Render previous button
 */
function renderPrevButton(chapter) {
    if (!chapter.prev) {
        return '<div class="nav-button disabled"><span>← No Previous Chapter</span></div>';
    }
    
    const prevChapter = CHAPTERS[chapter.prev];
    return `
        <a href="#${chapter.prev}" class="nav-button" data-nav="prev">
            <div>
                <span class="nav-label">← Previous</span>
                <div class="nav-title">${prevChapter.title}</div>
            </div>
        </a>
    `;
}

/**
 * Render next button
 */
function renderNextButton(chapter) {
    if (!chapter.next) {
        return '<div class="nav-button disabled"><span>No Next Chapter →</span></div>';
    }
    
    const nextChapter = CHAPTERS[chapter.next];
    return `
        <a href="#${chapter.next}" class="nav-button" data-nav="next">
            <div style="text-align: right;">
                <span class="nav-label">Next →</span>
                <div class="nav-title">${nextChapter.title}</div>
            </div>
        </a>
    `;
}

/**
 * Setup chapter navigation button listeners
 */
function setupChapterNavButtons() {
    const navButtons = document.querySelectorAll('[data-nav]');
    navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const chapterId = button.getAttribute('href').slice(1);
            window.location.hash = chapterId;
            loadChapter(chapterId);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

/**
 * Update sidebar active state
 */
function updateSidebarActive(chapterId) {
    const links = document.querySelectorAll('.chapter-link');
    links.forEach(link => {
        if (link.dataset.chapter === chapterId) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Show loading state
 */
function showLoading() {
    const container = document.getElementById('chapterContent');
    container.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Loading chapter...</p>
        </div>
    `;
}

/**
 * Show error state
 */
function showError(message) {
    const container = document.getElementById('chapterContent');
    container.innerHTML = `
        <div class="chapter-container">
            <div style="text-align: center; padding: 4rem 2rem;">
                <h2 style="color: var(--danger); margin-bottom: 1rem;">⚠️ Error</h2>
                <p style="color: var(--text-secondary);">${message}</p>
                <a href="#prologue" style="display: inline-block; margin-top: 2rem; padding: 1rem 2rem; background: var(--accent-primary); color: white; text-decoration: none; border-radius: var(--radius-md);">Return to Prologue</a>
            </div>
        </div>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
