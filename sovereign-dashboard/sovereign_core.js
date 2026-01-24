/**
 * 🧬 SOVEREIGN CORE JS v14.0 - Enhanced Navigation System
 * ========================================================
 * Unified navigation, state management, and cross-UI orchestration
 * for the aSiReM Sovereign Ecosystem.
 */

class SovereignCore {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.sidebarExpanded = localStorage.getItem('sidebarExpanded') !== 'false';
        this.currentJourney = localStorage.getItem('lastJourney') || 'discovery';
        this.agentStatus = {};

        this.init();
    }

    init() {
        console.log("🧬 Sovereign Core v14.0 Initialized");
        this.injectSidebar();
        this.injectBreadcrumb();
        this.applyGlobalStyles();
        this.setupKeyboardShortcuts();
        this.connectWebSocket();
    }

    // ============================================================================
    // NAVIGATION STRUCTURE
    // ============================================================================

    getNavigationTree() {
        return [
            {
                id: 'gateway',
                icon: '🏠',
                label: 'Gateway',
                url: '/',
                description: 'Main entry point'
            },
            {
                id: 'discovery',
                icon: '🔍',
                label: 'Discovery',
                description: 'Understand your codebase',
                children: [
                    { id: 'network-topology', icon: '🕸️', label: 'Agent Network', url: '/discovery' },
                    { id: 'discovery-matrix', icon: '🌌', label: 'Discovery Matrix', url: '/web-ui/index.html' },
                    { id: 'command-center', icon: '🛰️', label: 'Command Center', url: '/dashboard' }
                ]
            },
            {
                id: 'architecture',
                icon: '🏗️',
                label: 'Architecture',
                description: 'Design and plan solutions',
                children: [
                    { id: 'zen-architect', icon: '⛩️', label: 'ZenArchitect', url: '/dashboard#zen-architect' },
                    { id: 'nebula', icon: '🌠', label: 'Nebula Orchestrator', url: '/dashboard#nebula' },
                    { id: 'api-workbench', icon: '🔧', label: 'API Workbench', url: '/dashboard#api-workbench' }
                ]
            },
            {
                id: 'actuation',
                icon: '⚡',
                label: 'Actuation',
                description: 'Execute and deploy',
                children: [
                    { id: 'task-dashboard', icon: '🎯', label: 'Task Dashboard', url: '/actuation' },
                    { id: 'bytebot', icon: '🤖', label: 'ByteBot Desktop', url: '/dashboard#bytebot' },
                    { id: 'voice-commands', icon: '🎙️', label: 'Voice Commands', url: '/dashboard#voice' }
                ]
            },
            {
                id: 'observability',
                icon: '🔭',
                label: 'Observability',
                url: '/observability',
                description: 'Monitor system health'
            }
        ];
    }

    // ============================================================================
    // SIDEBAR INJECTION
    // ============================================================================

    injectSidebar() {
        if (document.getElementById('sovereign-sidebar')) return;

        const sidebar = document.createElement('div');
        sidebar.id = 'sovereign-sidebar';
        sidebar.className = `sovereign-sidebar ${this.sidebarExpanded ? 'expanded' : 'collapsed'}`;

        const navTree = this.getNavigationTree();

        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <span class="logo-icon">🧬</span>
                    <span class="logo-text">aSiReM</span>
                </div>
                <button class="sidebar-toggle" id="sidebarToggle" aria-label="Toggle sidebar">
                    <span class="toggle-icon">◀</span>
                </button>
            </div>
            
            <nav class="sidebar-nav">
                ${navTree.map(item => this.renderNavItem(item)).join('')}
            </nav>
            
            <div class="sidebar-footer">
                <div class="agent-status-summary" id="agentStatusSummary">
                    <span class="status-dot"></span>
                    <span class="status-text">Connecting...</span>
                </div>
                <div class="version-info">v14.0</div>
            </div>
        `;

        document.body.appendChild(sidebar);

        document.body.appendChild(sidebar);

        // Adjust body padding and set CSS variable
        document.body.style.position = 'relative';
        document.body.style.transition = 'padding-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        this.updateLayout();

        // Setup event listeners
        this.setupSidebarEvents();
    }

    updateLayout() {
        const width = this.sidebarExpanded ? '280px' : '80px';
        document.body.style.paddingLeft = width;
        document.documentElement.style.setProperty('--sidebar-width', width);
    }

    renderNavItem(item, level = 0) {
        const hasChildren = item.children && item.children.length > 0;
        const isActive = this.isCurrentPath(item.url) || (item.id === this.currentJourney);
        const isExpanded = localStorage.getItem(`nav-${item.id}-expanded`) !== 'false';

        let html = `
            <div class="nav-item ${isActive ? 'active' : ''} level-${level}" data-nav-id="${item.id}">
                <div class="nav-item-content" ${item.url ? `onclick="sovereignNavigate('${item.url}')"` : ''}>
                    <span class="nav-icon">${item.icon}</span>
                    <span class="nav-label">${item.label}</span>
                    ${hasChildren ? `<span class="nav-expand ${isExpanded ? 'expanded' : ''}" onclick="event.stopPropagation(); sovereignToggleNav('${item.id}')">▸</span>` : ''}
                </div>
                ${item.description ? `<div class="nav-description">${item.description}</div>` : ''}
        `;

        if (hasChildren) {
            html += `
                <div class="nav-children ${isExpanded ? 'expanded' : 'collapsed'}" id="nav-${item.id}-children">
                    ${item.children.map(child => this.renderNavItem(child, level + 1)).join('')}
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    setupSidebarEvents() {
        const toggleBtn = document.getElementById('sidebarToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleSidebar());
        }
    }

    toggleSidebar() {
        this.sidebarExpanded = !this.sidebarExpanded;
        localStorage.setItem('sidebarExpanded', this.sidebarExpanded);

        const sidebar = document.getElementById('sovereign-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('expanded', this.sidebarExpanded);
            sidebar.classList.toggle('collapsed', !this.sidebarExpanded);
        }

        const toggleIcon = document.querySelector('.toggle-icon');
        if (toggleIcon) {
            toggleIcon.textContent = this.sidebarExpanded ? '◀' : '▶';
        }

        if (toggleIcon) {
            toggleIcon.textContent = this.sidebarExpanded ? '◀' : '▶';
        }

        // Adjust layout
        this.updateLayout();
    }

    // ============================================================================
    // BREADCRUMB TRAIL
    // ============================================================================

    injectBreadcrumb() {
        if (document.getElementById('sovereign-breadcrumb')) return;

        const breadcrumb = document.createElement('div');
        breadcrumb.id = 'sovereign-breadcrumb';
        breadcrumb.className = 'sovereign-breadcrumb';

        const trail = this.getBreadcrumbTrail();
        breadcrumb.innerHTML = trail.map((item, index) => `
            <span class="breadcrumb-item ${index === trail.length - 1 ? 'active' : ''}" 
                  ${item.url ? `onclick="sovereignNavigate('${item.url}')"` : ''}>
                ${item.icon} ${item.label}
            </span>
            ${index < trail.length - 1 ? '<span class="breadcrumb-separator">›</span>' : ''}
        `).join('');

        document.body.appendChild(breadcrumb);
    }

    getBreadcrumbTrail() {
        const path = window.location.pathname;
        const hash = window.location.hash;

        // Simple breadcrumb logic - can be enhanced
        const trail = [{ icon: '🏠', label: 'Gateway', url: '/gateway.html' }];

        if (path.includes('index.html')) {
            trail.push({ icon: '🔍', label: 'Discovery' });

            if (hash.includes('zen-architect')) {
                trail.push({ icon: '⛩️', label: 'ZenArchitect' });
            } else if (hash.includes('nebula')) {
                trail.push({ icon: '🌠', label: 'Nebula' });
            } else if (hash.includes('bytebot')) {
                trail.push({ icon: '🤖', label: 'ByteBot' });
            }
        }

        return trail;
    }

    // ============================================================================
    // WEBSOCKET CONNECTION
    // ============================================================================

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/stream`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('✅ Sovereign Core WebSocket connected');
                this.updateAgentStatus('connected', 'Sovereign Core Online');
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ Sovereign Core WebSocket error:', error);
                this.updateAgentStatus('error', 'Connection Error');
            };

            this.ws.onclose = () => {
                console.log('🔌 Sovereign Core WebSocket disconnected');
                this.updateAgentStatus('connecting', 'Reconnecting...');

                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => this.connectWebSocket(), 2000 * this.reconnectAttempts);
                } else {
                    this.updateAgentStatus('error', 'Connection Failed');
                }
            };
        } catch (e) {
            console.error('Failed to create WebSocket:', e);
            this.updateAgentStatus('error', 'Connection Failed');
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'agent_status') {
            this.agentStatus = data.agents || {};
            this.updateAgentStatusDisplay();
        } else if (data.type === 'system_status') {
            this.updateAgentStatus('connected', data.message || 'System Ready');
        } else if (data.type === 'navigation') {
            // Handle cross-UI navigation commands
            if (data.target) {
                this.navigate(data.target);
            }
        }
    }

    updateAgentStatus(state, message) {
        const statusSummary = document.getElementById('agentStatusSummary');
        if (!statusSummary) return;

        const statusDot = statusSummary.querySelector('.status-dot');
        const statusText = statusSummary.querySelector('.status-text');

        if (statusDot) {
            statusDot.className = 'status-dot';
            if (state === 'connecting') statusDot.classList.add('connecting');
            else if (state === 'error') statusDot.classList.add('error');
            else statusDot.classList.add('connected');
        }

        if (statusText) {
            statusText.textContent = message;
        }
    }

    updateAgentStatusDisplay() {
        const activeCount = Object.values(this.agentStatus).filter(s => s === 'active').length;
        this.updateAgentStatus('connected', `${activeCount} agents active`);
    }

    // ============================================================================
    // NAVIGATION HELPERS
    // ============================================================================

    isCurrentPath(url) {
        if (!url) return false;
        if (url === '/' && window.location.pathname === '/') return true;
        if (url !== '/' && window.location.pathname.includes(url)) return true;
        return false;
    }

    navigate(url) {
        console.log(`🧭 Navigating to: ${url}`);

        // Store navigation history
        const history = JSON.parse(localStorage.getItem('navHistory') || '[]');
        history.push({ url, timestamp: Date.now() });
        if (history.length > 50) history.shift();
        localStorage.setItem('navHistory', JSON.stringify(history));

        // Navigate
        window.location.href = url;
    }

    // ============================================================================
    // KEYBOARD SHORTCUTS
    // ============================================================================

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B: Toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }

            // Ctrl/Cmd + H: Go to gateway
            if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
                e.preventDefault();
                this.navigate('/gateway.html');
            }

            // Ctrl/Cmd + 1-4: Quick navigation
            if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '4') {
                e.preventDefault();
                const journeys = ['discovery', 'architecture', 'actuation', 'observability'];
                const journey = journeys[parseInt(e.key) - 1];
                this.navigate(`/index.html#${journey}`);
            }
        });
    }

    // ============================================================================
    // GLOBAL STYLES
    // ============================================================================

    applyGlobalStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Adjust body padding for sidebar */
            body {
                padding-left: 280px;
                padding-top: 50px;
                transition: padding-left 0.3s ease;
            }
            
            body:has(.sovereign-sidebar.collapsed) {
                padding-left: 80px;
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                body {
                    padding-left: 0 !important;
                    padding-bottom: 70px;
                }
                
                .sovereign-sidebar {
                    bottom: 0;
                    left: 0;
                    right: 0;
                    top: auto !important;
                    width: 100% !important;
                    height: 70px;
                    flex-direction: row !important;
                    border-right: none !important;
                    border-top: 1px solid rgba(255,255,255,0.1);
                }
                
                .sidebar-header,
                .sidebar-footer,
                .nav-description,
                .nav-children {
                    display: none !important;
                }
                
                .sidebar-nav {
                    flex-direction: row !important;
                    justify-content: space-around;
                    width: 100%;
                }
                
                .nav-label {
                    display: none !important;
                }
                
                .sovereign-breadcrumb {
                    display: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // ============================================================================
    // GLOBAL EVENT HANDLER
    // ============================================================================

    static handleEvent(event) {
        console.log("Sovereign Event:", event);

        // Dispatch custom events for other components to listen to
        window.dispatchEvent(new CustomEvent('sovereign:event', { detail: event }));
    }
}

// ============================================================================
// GLOBAL HELPER FUNCTIONS
// ============================================================================

function sovereignNavigate(url) {
    if (window.sovereign) {
        window.sovereign.navigate(url);
    } else {
        window.location.href = url;
    }
}

function sovereignToggleNav(navId) {
    const children = document.getElementById(`nav-${navId}-children`);
    const expand = document.querySelector(`[data-nav-id="${navId}"] .nav-expand`);

    if (children && expand) {
        const isExpanded = children.classList.toggle('expanded');
        children.classList.toggle('collapsed', !isExpanded);
        expand.classList.toggle('expanded', isExpanded);

        localStorage.setItem(`nav-${navId}-expanded`, isExpanded);
    }
}

// ============================================================================
// AUTO-INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    window.sovereign = new SovereignCore();
    console.log('🚀 Sovereign Core ready');
});
