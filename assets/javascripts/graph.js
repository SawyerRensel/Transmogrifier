// material/plugins/graph/assets/javascripts/graph.js
document.addEventListener("DOMContentLoaded", async function () {
    const baseUrl = window.graph_base_url || "";
    const dataUrl = (baseUrl && !baseUrl.endsWith("/")) ? baseUrl + "/graph.json" : baseUrl + "graph.json";
    const currentPage = window.graph_current_page || "";
    const config = window.graph_config || {};

    // Default configuration
    const graphConfig = {
        local_graph_depth: config.local_graph_depth || 1,
        global_graph: config.global_graph !== false,
        repel_force: config.repel_force || 1.0,
        center_force: config.center_force || 0.2,
        link_distance: config.link_distance || 50,
        scale: config.scale || 1.1,
        font_size: config.font_size || 10,
        show_tags: config.show_tags || false,
        enable_drag: config.enable_drag !== false,
        enable_zoom: config.enable_zoom !== false,
        focus_on_hover: config.focus_on_hover !== false
    };

    let graphData = null;

    try {
        const response = await fetch(dataUrl);
        if (!response.ok) throw new Error("Failed to load graph data");
        graphData = await response.json();
    } catch (e) {
        console.error("Graph load error:", e);
        return;
    }

    // --- Inject Mini Graph Container ---
    // Check if we're on mobile (no sidebar visible or narrow viewport)
    const isMobile = window.innerWidth < 1220;
    const sidebar = document.querySelector(".md-sidebar--secondary .md-sidebar__inner");

    let miniContainer = document.createElement("div");
    miniContainer.id = "mini-graph-container";

    const expandBtn = document.createElement("button");
    expandBtn.id = "mini-graph-expand";
    expandBtn.title = "Expand Graph";
    expandBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M5,5H10V7H7V10H5V5M14,5H19V10H17V7H14V5M17,14H19V19H14V17H17V14M10,17V19H5V14H7V17H10Z" /></svg>';
    miniContainer.appendChild(expandBtn);

    if (isMobile || !sidebar) {
        // Mobile: place at bottom of main content
        miniContainer.classList.add("mini-graph-mobile");
        const mainContent = document.querySelector(".md-content__inner");
        if (mainContent) {
            mainContent.appendChild(miniContainer);
        }
    } else {
        // Desktop: place in sidebar
        if (sidebar.firstChild) {
            sidebar.insertBefore(miniContainer, sidebar.firstChild);
        } else {
            sidebar.appendChild(miniContainer);
        }
    }

    initGraph(miniContainer, graphData, { isMini: true, currentPage: currentPage, config: graphConfig });

    expandBtn.addEventListener("click", () => {
        openFullGraph();
    });

    // --- Handle window resize for responsive layout ---
    let resizeTimeout;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const newIsMobile = window.innerWidth < 1220;
            const currentIsMobile = miniContainer.classList.contains("mini-graph-mobile");

            // Only reposition if mobile state changed
            if (newIsMobile !== currentIsMobile) {
                const mainContent = document.querySelector(".md-content__inner");
                const sidebarInner = document.querySelector(".md-sidebar--secondary .md-sidebar__inner");

                if (newIsMobile || !sidebarInner) {
                    // Switch to mobile layout
                    miniContainer.classList.add("mini-graph-mobile");
                    if (mainContent && !mainContent.contains(miniContainer)) {
                        mainContent.appendChild(miniContainer);
                    }
                } else {
                    // Switch to desktop layout
                    miniContainer.classList.remove("mini-graph-mobile");
                    if (sidebarInner && !sidebarInner.contains(miniContainer)) {
                        if (sidebarInner.firstChild) {
                            sidebarInner.insertBefore(miniContainer, sidebarInner.firstChild);
                        } else {
                            sidebarInner.appendChild(miniContainer);
                        }
                    }
                }

                // Clear and reinitialize the graph to reset zoom/pan state
                miniContainer.innerHTML = "";
                miniContainer.appendChild(expandBtn);
                initGraph(miniContainer, graphData, { isMini: true, currentPage: currentPage, config: graphConfig });
            }
        }, 250); // Debounce resize events
    });

    // --- Inject Full Graph Overlay ---
    const overlay = document.createElement("div");
    overlay.id = "graph-overlay";
    const fullContainer = document.createElement("div");
    fullContainer.id = "graph-container";

    // Add close button
    const closeBtn = document.createElement("button");
    closeBtn.id = "graph-close";
    closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" /></svg>';
    closeBtn.title = "Close Graph";
    fullContainer.appendChild(closeBtn);

    overlay.appendChild(fullContainer);
    document.body.appendChild(overlay);

    closeBtn.addEventListener("click", () => {
        overlay.style.display = "none";
    });

    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
            overlay.style.display = "none";
        }
    });

    let fullGraphInitialized = false;

    function openFullGraph() {
        overlay.style.display = "flex";
        if (!fullGraphInitialized) {
            initGraph(fullContainer, graphData, { isMini: false, currentPage: currentPage, config: graphConfig });
            fullGraphInitialized = true;
        }
    }

    // --- Core Graph Logic ---
    function initGraph(container, data, options) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        const isMini = options.isMini;
        const currentPage = options.currentPage;
        const cfg = options.config;

        let nodes = data.nodes.map(d => Object.create(d));
        let links = data.links.map(d => Object.create(d));

        // Filter for Mini Graph with configurable depth
        if (isMini) {
            const depth = cfg.local_graph_depth;
            const neighborIds = new Set();

            // Build adjacency map
            const adjacency = new Map();
            links.forEach(l => {
                if (!adjacency.has(l.source)) adjacency.set(l.source, []);
                if (!adjacency.has(l.target)) adjacency.set(l.target, []);
                adjacency.get(l.source).push(l.target);
                adjacency.get(l.target).push(l.source);
            });

            // Check if current page exists
            // Note: currentPage can be empty string "" for homepage, which is a valid page ID
            if (currentPage !== null && currentPage !== undefined) {
                // Always show the current page
                neighborIds.add(currentPage);

                // If the page has connections, perform BFS to find connected nodes
                if (adjacency.has(currentPage)) {
                    const queue = [{ id: currentPage, dist: 0 }];
                    const visited = new Set([currentPage]);

                    while (queue.length > 0) {
                        const { id, dist } = queue.shift();
                        if (dist < depth && adjacency.has(id)) {
                            for (const neighbor of adjacency.get(id)) {
                                if (!visited.has(neighbor)) {
                                    visited.add(neighbor);
                                    neighborIds.add(neighbor);
                                    queue.push({ id: neighbor, dist: dist + 1 });
                                }
                            }
                        }
                    }
                }
                // If no connections, neighborIds only contains currentPage (shows single node)

                nodes = nodes.filter(n => neighborIds.has(n.id));
                links = links.filter(l => neighborIds.has(l.source) && neighborIds.has(l.target));
            } else {
                // No current page defined - show empty graph
                nodes = [];
                links = [];
            }
        }

        const svg = d3.select(container).append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", [0, 0, width, height]);

        const g = svg.append("g");

        // Apply zoom if enabled
        if (cfg.enable_zoom) {
            const zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on("zoom", ({ transform }) => {
                    g.attr("transform", transform);
                });
            svg.call(zoom);
        }

        // Configure physics simulation
        const repelForce = isMini ? -40 : (-50 * cfg.repel_force);
        const linkDist = isMini ? 50 : cfg.link_distance;
        const centerForce = cfg.center_force;

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(linkDist))
            .force("charge", d3.forceManyBody().strength(repelForce))
            .force("center", d3.forceCenter(width / 2, height / 2).strength(centerForce))
            .force("collide", d3.forceCollide().radius(isMini ? 12 : 12));

        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "graph-link");

        const nodeGroup = g.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .join("g");

        // Apply drag if enabled
        if (cfg.enable_drag) {
            nodeGroup.call(drag(simulation));
        }

        const circle = nodeGroup.append("circle")
            .attr("class", "graph-node")
            .attr("r", isMini ? 4 : 6)
            .classed("active", d => d.id === currentPage); // Highlight current page

        const label = nodeGroup.append("text")
            .attr("class", "graph-label")
            .attr("text-anchor", "middle")
            .attr("dy", isMini ? -10 : -12)
            .style("font-size", `${cfg.font_size}px`)
            .text(d => {
                let text = d.title;
                if (cfg.show_tags && d.tags && d.tags.length > 0) {
                    text += ` [${d.tags.join(', ')}]`;
                }
                return text;
            });

        nodeGroup.on("click", (event, d) => {
            const target = (window.graph_base_url || "") + d.id;
            window.location.href = target;
        });

        // Add hover effects if enabled
        if (cfg.focus_on_hover) {
            nodeGroup.on("mouseover", function (event, d) {
                d3.select(this).select("circle").attr("r", isMini ? 6 : 9);
                link.style("stroke-opacity", l => (l.source === d || l.target === d) ? 1 : 0.1);

                // Highlight connected nodes
                nodeGroup.each(function(n) {
                    const isConnected = n === d ||
                        links.some(l => (l.source === d && l.target === n) || (l.target === d && l.source === n));
                    d3.select(this).style("opacity", isConnected ? 1 : 0.3);
                });
            })
            .on("mouseout", function (event, d) {
                d3.select(this).select("circle").attr("r", isMini ? 4 : 6);
                link.style("stroke-opacity", 0.4);
                nodeGroup.style("opacity", 1);
            });
        }

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            nodeGroup
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });
    }

    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }
});
