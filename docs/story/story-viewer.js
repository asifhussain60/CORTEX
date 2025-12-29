/**
 * CORTEX Story Viewer - Interactive Chapter Navigation
 * Author: Asif Hussain
 * Copyright © 2025 Asif Hussain. All rights reserved.
 */

// Track last speaker for conversation flow (dialogue coloring)
let lastSpeaker = null;

// Chapter Configuration with Images
const CHAPTERS = {
    'prologue': {
        id: 'prologue',
        number: 'PROLOGUE',
        title: 'The Basement Laboratory',
        file: 'Prologue/index.html',
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
        file: 'Chapter-01/index.html',
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
        file: 'Chapter-02/index.html',
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
        file: 'Chapter-03/index.html',
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch03-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch03-02.jpeg', position: 'right' }
        ],
        next: 'chapter-04',
        prev: 'chapter-02'
    },
    'chapter-04': {
        id: 'chapter-04',
        number: 'CHAPTER 4',
        title: 'Tier 2 - The Learning Machine',
        file: 'Chapter-04/index.html',
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch04-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch04-02.jpeg', position: 'right' }
        ],
        next: 'chapter-05',
        prev: 'chapter-03'
    },
    'chapter-05': {
        id: 'chapter-05',
        number: 'CHAPTER 5',
        title: 'The Test-Driven Rebellion',
        file: 'Chapter-05/index.html',
        images: [
            { src: 'illustrations/images/valuable/cortex-awakening-ch05-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch05-02.jpeg', position: 'right' }
        ],
        next: 'chapter-06',
        prev: 'chapter-04'
    },
    'chapter-06': {
        id: 'chapter-06',
        number: 'CHAPTER 6',
        title: 'The Great Orchestration',
        file: 'Chapter-06/index.html',
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch06-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch06-01.jpeg', position: 'right' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch06-02.jpeg', position: 'left' }
        ],
        next: 'chapter-07',
        prev: 'chapter-05'
    },
    'chapter-07': {
        id: 'chapter-07',
        number: 'CHAPTER 7',
        title: 'The Planning Revolution',
        file: 'Chapter-07/index.html',
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
        file: 'Chapter-08/index.html',
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch08-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch08-02.jpeg', position: 'right' }
        ],
        next: 'chapter-09',
        prev: 'chapter-07'
    },
    'chapter-09': {
        id: 'chapter-09',
        number: 'CHAPTER 9',
        title: 'The Sanitizer\'s Dilemma',
        file: 'Chapter-09/index.html',
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
        file: 'Chapter-10/index.html',
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
        file: 'Chapter-11/index.html',
        images: [
            { src: 'illustrations/images/essentials/cortex-awakening-ch11-01.jpeg', position: 'left' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch11-01.jpeg', position: 'right' },
            { src: 'illustrations/images/valuable/cortex-awakening-ch11-02.jpeg', position: 'left' }
        ],
        next: 'chapter-12',
        prev: 'chapter-10'
    },
    'chapter-12': {
        id: 'chapter-12',
        number: 'CHAPTER 12',
        title: 'The Convergence',
        file: 'Chapter-12/index.html',
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
        file: 'Chapter-13/index.html',
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
    // Check URL hash for chapter
    const hash = window.location.hash.slice(1);
    
    // Setup mobile menu
    setupMobileMenu();
    
    // Setup navigation listeners first
    setupNavigation();
    
    // Load initial view - show mobile welcome or chapter
    if (hash) {
        loadChapter(hash);
    } else {
        showInitialView();
    }

    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
        const newHash = window.location.hash.slice(1);
        if (newHash) {
            loadChapter(newHash);
        } else {
            showInitialView();
        }
    });
}

/**
 * Setup mobile menu functionality
 */
function setupMobileMenu() {
    const burgerMenu = document.getElementById('burgerMenu');
    const sidebar = document.getElementById('chapterSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!burgerMenu || !sidebar || !overlay) return;
    
    // Toggle sidebar on burger click
    burgerMenu.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    });
    
    // Close sidebar on overlay click
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    });
    
    // Close sidebar when chapter link is clicked (mobile)
    const chapterLinks = document.querySelectorAll('.chapter-link');
    chapterLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }
        });
    });
}

/**
 * Show initial view (title cover on desktop, mobile welcome on mobile)
 */
function showInitialView() {
    if (window.innerWidth <= 768) {
        showMobileWelcome();
    } else {
        showTitleCover();
    }
}

/**
 * Show mobile welcome screen
 */
function showMobileWelcome() {
    const container = document.getElementById('chapterContent');
    
    // Clear all active states in sidebar
    const links = document.querySelectorAll('.chapter-link');
    links.forEach(link => link.classList.remove('active'));
    
    // Display mobile-friendly welcome screen
    container.innerHTML = `
        <div class="mobile-welcome">
            <h1>🧠 The Awakening of CORTEX</h1>
            <a href="#prologue" class="mobile-welcome-button">Start Reading</a>
            <img 
                src="illustrations/images/TitleCover.png" 
                alt="The Awakening of CORTEX - Title Cover" 
                class="mobile-welcome-image"
                onerror="this.style.display='none';"
            />
        </div>
    `;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
 * Show the title cover image (when no chapter selected)
 */
function showTitleCover() {
    const container = document.getElementById('chapterContent');
    
    // Clear all active states in sidebar
    const links = document.querySelectorAll('.chapter-link');
    links.forEach(link => link.classList.remove('active'));
    
    // Display centered title cover with fade-in animation
    container.innerHTML = `
        <div class="title-cover-container">
            <img 
                src="illustrations/images/TitleCover.png" 
                alt="The Awakening of CORTEX - Title Cover" 
                class="title-cover-image"
                onload="this.style.opacity='1'"
                onerror="this.src=''; this.alt='Title cover image not found'; this.style.border='2px dashed var(--glass-border)'; this.style.padding='4rem'; this.style.color='var(--text-secondary);'"
            />
        </div>
        <style>
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
        </style>
    `;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
    
    // Detect if content is already HTML (starts with <!DOCTYPE or <html>)
    let html;
    if (content.trim().startsWith('<!DOCTYPE') || content.trim().startsWith('<html')) {
        // Extract body content from HTML file
        const bodyMatch = content.match(/<body[^>]*>([\s\S]*)<\/body>/i);
        if (bodyMatch) {
            html = bodyMatch[1];
        } else {
            html = content;
        }
    } else {
        // Parse markdown content with embedded images
        html = parseChapterContent(content, chapter.images || []);
    }
    
    // Build chapter HTML
    const chapterHTML = `
        <div class="chapter-container">
            <div class="chapter-header">
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
    // Strip frontmatter (YAML between ---) and HTML wrapper tags
    let lines = text.split('\n');
    
    // Remove YAML frontmatter
    if (lines[0] === '---') {
        const endIndex = lines.findIndex((line, i) => i > 0 && line === '---');
        if (endIndex > 0) {
            lines = lines.slice(endIndex + 1);
        }
    }
    
    // Remove HTML wrapper tags and link tags (but keep empty lines for paragraph separation)
    lines = lines.filter(line => {
        const trimmed = line.trim();
        // Keep empty lines
        if (trimmed === '') return true;
        // Filter out HTML wrapper elements and navigation
        return !trimmed.startsWith('<link ') && 
               !trimmed.startsWith('<div class="story-') &&
               !trimmed.startsWith('<div class="chapter-navigation') &&
               !trimmed.startsWith('<a href=') &&
               trimmed !== '</div>' &&
               trimmed !== '</a>';
    });
    
    // Remove first line if it's the chapter title (starts with #)
    if (lines[0] && lines[0].trim().startsWith('# ')) {
        lines = lines.slice(1);
    }
    
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
            // Reset speaker tracking at section boundaries
            lastSpeaker = null;
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
            // Reset speaker tracking at subsection boundaries
            lastSpeaker = null;
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
            html += '<hr class="story-hr">';
            continue;
        }
        
        // Embedded image tag (HTML img tag in markdown)
        if (line.startsWith('<img ')) {
            if (inParagraph) {
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            // Fix relative paths: ../illustrations/ → illustrations/
            line = line.replace(/src=["']\.\.\/illustrations\//g, 'src="illustrations/');
            html += line; // Pass through HTML img tags
            continue;
        }
        
        // Markdown-style image: ![alt](path)
        if (line.match(/^!\[.*\]\(.+\)$/)) {
            if (inParagraph) {
                html += processCharacterDialog(paragraphBuffer) + '</p>';
                paragraphBuffer = '';
                inParagraph = false;
            }
            // Convert markdown image to HTML and skip (these are often placeholders)
            // Match: ![alt text](path)
            const match = line.match(/^!\[(.*?)\]\((.+?)\)$/);
            if (match) {
                const alt = match[1];
                let src = match[2];
                // Fix relative paths
                src = src.replace(/^\.\.\/illustrations\//, 'illustrations/');
                src = src.replace(/^images\//, 'illustrations/images/');
                html += `<div class="chapter-image"><img src="${src}" alt="${alt}" class="chapter-image" /></div>`;
            }
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
 * Process character dialog with consistent color coding using CSS classes
 * Detects character names and applies appropriate CSS class
 * SIMPLIFIED: Two-color system for clear distinction
 */
function processCharacterDialog(text) {
    // Character to CSS class mapping
    const characterClasses = {
        'Asif': 'dialogue-asif',
        'Miss G': 'dialogue-miss-g',
        'Copilot': 'dialogue-copilot',
        'CORTEX': 'dialogue-cortex',
        'client': 'dialogue-client',
        'Mom': 'dialogue-miss-g',    // Group with Miss G
        'he': 'dialogue-asif',       // Asif (pronoun)
        'He': 'dialogue-asif',
        'his': 'dialogue-asif',
        'His': 'dialogue-asif',
        'she': 'dialogue-miss-g',    // Miss G (pronoun)
        'She': 'dialogue-miss-g',
        'her': 'dialogue-miss-g',
        'Her': 'dialogue-miss-g'
    };
    
    // Process quoted dialog with character detection
    text = text.replace(/"([^"]+)"/g, (match, dialog, offset) => {
        // Skip meta-content (HTML attributes, CSS, file paths)
        if (dialog.includes('://') || dialog.includes('.css') || dialog.includes('.jpeg') || 
            dialog.includes('.png') || dialog.includes('Chapter') || dialog.includes('float:') ||
            dialog.includes('margin:') || dialog.includes('max-width') || dialog.includes('story-')) {
            return match; // Return uncolored
        }
        
        // Get context before the quote (up to 300 chars for better detection)
        const contextBefore = text.substring(Math.max(0, offset - 300), offset);
        
        // Get context after the quote (up to 150 chars for "said" attribution)
        const contextAfter = text.substring(offset + match.length, Math.min(text.length, offset + match.length + 150));
        
        // First-person narrator detection (Asif is the narrator)
        // Check BEFORE the quote
        const firstPersonPatternsBefore = [
            /\bI\s+(?:said|asked|responded|replied|muttered|whispered|thought|wondered|froze|looked|turned|spun|gestured|pointed|ran|spun back|tried|managed|let|continued|stopped|started)/i,
            /\bMy\s+(?:voice|thoughts|mind|hand|hands|eyes|face|head)/i,
            /\bI\s+(?:could|would|should|had to|needed to|wanted to)/i
        ];
        
        for (const pattern of firstPersonPatternsBefore) {
            if (pattern.test(contextBefore)) {
                lastSpeaker = 'Asif';
                return `<span class="dialogue-asif">"${dialog}"</span>`;
            }
        }
        
        // Check AFTER the quote for trailing attribution (e.g., "text," I said)
        const firstPersonPatternsAfter = [
            /^[,.]?\s*I\s+(?:said|asked|responded|replied|muttered|whispered|thought|wondered|froze|looked|turned|spun|gestured|pointed|ran|spun back|tried|managed|let|continued|stopped|started|typed|opened|pulled|set|took|added|explained|told|announced|declared)/i,
            /^[,.]?\s*My\s+(?:voice|thoughts|mind|hand|hands|eyes|face|head)/i
        ];
        
        for (const pattern of firstPersonPatternsAfter) {
            if (pattern.test(contextAfter)) {
                lastSpeaker = 'Asif';
                return `<span class="dialogue-asif">"${dialog}"</span>`;
            }
        }
        
            // Check which character is speaking based on context
        for (const [character, cssClass] of Object.entries(characterClasses)) {
            // Special handling for Miss G (imaginary girlfriend, inner voice)
            if (character === 'Miss G') {
                const missGPatterns = [
                    /Miss G'?s?\s+voice/i,
                    /(?:she|She)\s+used my full name/i,
                    /imaginary girlfriend/i,
                    /in my (?:thoughts|mind|consciousness|head)/i,
                    /(?:Mrs\.|Miss)\s*G'?s?\s*voice/i
                ];
                
                if (missGPatterns.some(p => p.test(contextBefore) || p.test(contextAfter))) {
                    lastSpeaker = 'Miss G';
                    return `<span class="${cssClass}">"${dialog}"</span>`;
                }
            }
            
            // Comprehensive pattern list to catch 70%+ unattributed dialogues
            const patterns = [
                // === DIRECT ATTRIBUTION ===
                // "Asif asked/said/muttered/whispered"
                new RegExp(`${character}[^.]*?$`, 'i'),
                
                // === POSSESSIVE FORMS ===
                // "Asif's voice/thoughts/mind"
                new RegExp(`${character}'s[^.]*?$`, 'i'),
                
                // === ACTION VERBS (Expanded) ===
                // Speech verbs
                new RegExp(`${character} (?:asked|said|responded|replied|explained|observed|suggested|confirmed|muttered|whispered|shouted|called|announced|added|continued|interrupted|stammered|blurted|declared|admitted|confessed|wondered|thought|mused|reflected|demanded|insisted|protested|argued|agreed|disagreed|corrected|clarified)`, 'i'),
                
                // Physical actions with dialogue
                new RegExp(`${character} (?:gestured|pointed|looked up|looked down|turned|stopped|ran|squinted|spun|spun back|spun around|leaned|stepped|walked|moved|sat|stood|nodded|shook|waved|grabbed|held|opened|closed|raised|lowered|lifted|dropped|pushed|pulled|reached|stretched)`, 'i'),
                
                // Emotional/mental actions
                new RegExp(`${character} (?:blinked|sighed|groaned|laughed|smiled|frowned|winced|flinched|hesitated|paused|waited|realized|noticed|recognized|remembered|forgot|wondered|worried|panicked|relaxed|tensed|softened|brightened|darkened)`, 'i'),
                
                // Temporal/modal markers
                new RegExp(`${character} (?:finally|eventually|suddenly|immediately|quickly|slowly|carefully|reluctantly|eagerly|desperately|nervously|confidently|quietly|loudly|gently|firmly|sharply|softly|barely|almost|just|already|still|now|then)`, 'i'),
                
                // === NEGATIVE/CONTRACTIONS ===
                new RegExp(`${character} (?:didn't|did|doesn't|don't|wasn't|weren't|isn't|aren't|couldn't|can't|wouldn't|won't|shouldn't|hasn't|haven't|hadn't)`, 'i'),
                
                // === CONTEXTUAL CLUES ===
                // "in his/her thoughts/mind/consciousness"
                new RegExp(`${character}[^.]{0,30}(?:thoughts|mind|consciousness|voice|presence|head|brain|heart|soul|memory|awareness|understanding)`, 'i'),
                
                // "His/Her [action]" patterns (possessive pronoun with action)
                new RegExp(`(?:His|Her|Their)[^.]{0,40}${character}`, 'i'),
                
                // === NARRATIVE CONTEXT ===
                // "[Character] could hear/see/feel"
                new RegExp(`${character} (?:could|would|should|might|must|had to|needed to|wanted to|tried to|began to|started to|continued to|managed to|failed to|seemed to|appeared to|tended to|used to|got to)`, 'i'),
                
                // === SENTENCE START ===
                // Catches "He muttered. 'text'" patterns
                new RegExp(`${character}[^."]*?\\.\\s*$`, 'i'),
                
                // === BODY LANGUAGE ===
                new RegExp(`${character}'s (?:hand|hands|eye|eyes|face|head|voice|expression|tone|demeanor|posture|body|fingers|lips|mouth|brow|forehead|shoulders|chest|arms|legs|feet)`, 'i'),
                
                // === STANDALONE/INTERNAL THOUGHTS ===
                // Character's internal monologue patterns (no explicit attribution nearby)
                new RegExp(`${character}[^.]{0,80}(?:thinking|wondering|realizing|noticing|questioning|understanding|knowing|feeling|sensing|believing|hoping|fearing|doubting)`, 'i'),
                
                // Multiple exclamations/capitals (emotional intensity = Asif style)
                character === 'he' && /[.!?]\s*[A-Z][A-Z\s]+[.!]/.test(contextBefore) ? /./ : null,
                
                // Basement/workspace context (Asif location markers)
                character === 'he' && /(?:basement|workspace|screen|keyboard|code|terminal|desk|chair|monitor|computer|laptop)/i.test(contextBefore) ? /./ : null,
                
                // === NARRATIVE FLOW MARKERS ===
                // Character referenced in subject position nearby
                new RegExp(`${character}(?:'s)?\\s+[a-z]+\\s+[^.]{0,50}$`, 'i'),
                
                // === PROXIMITY PATTERNS (NEW) ===
                // Character name appears within 2 sentences before quote
                new RegExp(`${character}[^.!?]{0,150}[.!?][^.!?]{0,150}$`, 'i'),
                
                // === DIALOGUE TAGS (NEW) ===
                // Common dialogue framing without explicit "said"
                new RegExp(`${character}[^.]{0,40}(?:spoke|called out|cried|yelled|screamed|whispered loudly|mumbled|grumbled|huffed|snapped|barked|growled)`, 'i'),
                
                // === SCENE CONTEXT (NEW) ===
                // Character is the active subject in the scene
                new RegExp(`${character}[^.]{0,60}(?:alone|by himself|by herself|in the|at the|from the|to the|with the|without)`, 'i'),
                
                // === MRS. G / MISS G PATTERNS (Special handling for AI voice) ===
                // "Mrs. G's voice" or "Miss G's voice over the speaker"
                (character === 'Miss G' || character === 'she') && /(?:Mrs\.|Miss)\s*G'?s?\s*voice/i.test(contextBefore) ? /./ : null,
                (character === 'Miss G' || character === 'she') && /over the speaker/i.test(contextBefore) ? /./ : null,
                (character === 'Miss G' || character === 'she') && /monitoring|observing/i.test(contextBefore) ? /./ : null,
                
                // === QUESTION-ANSWER PAIR DETECTION ===
                // If previous dialogue was a question and current is answer, alternate speaker
                // (This requires tracking previous speaker - simplified pattern)
                character === 'Miss G' && /\?"\s*$/.test(contextBefore) && !/(?:he|Asif)\s+(?:said|asked|responded)/i.test(contextBefore) ? /./ : null
            ].filter(Boolean);  // Remove null entries            // Check context AFTER quote for attribution (e.g., "text," he said)
            const patternsAfter = [
                // ", he said/asked/muttered" patterns
                new RegExp(`^[,.]?\\s*${character}\\s+(?:asked|said|responded|replied|muttered|whispered|shouted|thought|wondered|continued|added|observed|suggested|confirmed|blurted|stammered)`, 'i'),
                
                // Character action immediately after
                new RegExp(`^[,.]?\\s*${character}\\s+(?:blinked|sighed|nodded|turned|looked|smiled|frowned|winced)`, 'i')
            ];
            
            if (patterns.some(pattern => pattern && pattern.test(contextBefore)) || 
                patternsAfter.some(pattern => pattern.test(contextAfter))) {
                // Apply CSS class and track speaker
                lastSpeaker = character;
                return `<span class="${cssClass}">"${dialog}"</span>`;
            }
        }
        
        // Conversation flow: alternate speakers for short consecutive dialogues
        if (lastSpeaker && dialog.length < 50) {
            const alternativeSpeaker = lastSpeaker === 'Asif' ? 'Miss G' : 'Asif';
            const cssClass = characterClasses[alternativeSpeaker];
            
            // Verify no conflicting attribution in context
            const combinedContext = contextBefore + ' ' + contextAfter;
            const hasConflictingAttribution = /\b(Asif|Miss G|Copilot|CORTEX|client|Mom)\s+(?:asked|said|replied)/i.test(combinedContext);
            
            if (!hasConflictingAttribution) {
                lastSpeaker = alternativeSpeaker;
                return `<span class="${cssClass}">"${dialog}"</span>`;
            }
        }
        
        // Default dialog style (Asif's color for consistency)
        return `<span class="dialogue-default">"${dialog}"</span>`;
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
    const floatClass = position === 'right' ? 'float-right' : 'float-left';
    
    return `
        <div class="inline-image-wrapper ${floatClass}">
            <img src="${image.src}" 
                 alt="Story illustration" 
                 class="inline-image" />
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
    text = text.replace(/`(.+?)`/g, '<code class="inline-code">$1</code>');
    
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
            <div class="nav-next-content">
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
            <div class="error-container">
                <h2 class="error-title">⚠️ Error</h2>
                <p class="error-message">${message}</p>
                <a href="#prologue" class="error-link">Return to Prologue</a>
            </div>
        </div>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
