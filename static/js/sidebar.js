document.addEventListener("DOMContentLoaded", function () {
    const mainContent = document.getElementById("main-content");

    // Collapse all submodules initially
    document.querySelectorAll(".submodules").forEach(el => el.style.display = "none");

    // Toggle submodules on parent module click
    document.querySelectorAll(".sidebar-link.parent-module").forEach(parentLink => {
        parentLink.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent default anchor behavior
            const targetId = parentLink.dataset.toggle;
            const targetSub = document.getElementById(targetId);

            // Collapse all other submodules
            document.querySelectorAll(".submodules").forEach(sub => {
                if (sub.id !== targetId) {
                    sub.style.display = "none";
                    const otherParent = document.querySelector(`[data-toggle="${sub.id}"]`);
                    if (otherParent) {
                        const icon = otherParent.querySelector(".toggle-icon");
                        if (icon) icon.textContent = "expand_more";
                        otherParent.classList.remove("expanded");
                    }
                }
            });

            // Toggle the clicked submodule
            if (targetSub) {
                const isVisible = targetSub.style.display === "block";
                targetSub.style.display = isVisible ? "none" : "block";
                parentLink.classList.toggle("expanded", !isVisible);

                const icon = parentLink.querySelector(".toggle-icon");
                if (icon) {
                    icon.textContent = isVisible ? "expand_more" : "expand_less";
                }
            }
        });
    });

    // Load module function (no page reload)
    async function loadModule(moduleName, submoduleName) {
        if (!moduleName) return;

        const url = submoduleName 
            ? `/load_module/${moduleName}/${submoduleName}`
            : `/load_module/${moduleName}`;

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Module not found");

            const html = await response.text();
            mainContent.innerHTML = html;

            if (typeof window.setupThemeToggler === "function") {
            setupThemeToggler();
            }
            updateActiveLink(moduleName, submoduleName);
            history.pushState({ module: moduleName, submodule: submoduleName }, "", `?module=${moduleName}&submodule=${submoduleName || ""}`);

            // ✅ Load paginated project content
            if (moduleName === "projects" && (submoduleName === "ongoing" || submoduleName === "finished")) {
                try {
                    const { loadProjectTable } = await import('/static/js/common.js');
                    loadProjectTable(moduleName, submoduleName, 1);
                } catch (paginationErr) {
                    console.error("❌ Failed to load project table:", paginationErr);
                }
            }

            if (moduleName === "user_management") {
                setTimeout(() => {
                    if (typeof window.reloadUserTable === "function") {
                        window.reloadUserTable(1);
                    } else {
                        console.warn("❌ reloadUserTable is not defined yet");
                    }
                }, 50);
            }

            setTimeout(() => {
                window.initPagination?.();
                document.dispatchEvent(new CustomEvent("moduleLoaded", {
                    detail: { module: moduleName }
                }));
            }, 50);
        } catch (err) {
            console.error(err);
            mainContent.innerHTML = "<p>Error loading module.</p>";
        }
    }


    // Highlight the active link
    function updateActiveLink(moduleName, submoduleName) {
        document.querySelectorAll(".sidebar-link").forEach(link => {
            link.classList.remove("active");

            const isActive = link.dataset.module === moduleName &&
                (submoduleName ? link.dataset.submodule === submoduleName : !link.dataset.submodule);

            if (isActive) {
                link.classList.add("active");
            }
        });
    }

    // Attach click listeners to all module/submodule links (non-parent)
    document.querySelectorAll(".sidebar-link").forEach(link => {
        if (link.classList.contains("parent-module")) return;

        link.addEventListener("click", function (e) {
            const module = link.dataset.module;
            const submodule = link.dataset.submodule;
            if (!module) return;
            e.preventDefault();
            loadModule(module, submodule);
        });
    });

    // On refresh, load module if in URL
    const params = new URLSearchParams(window.location.search);
    const initialModule = params.get("module");
    const initialSubmodule = params.get("submodule");
    if (initialModule) loadModule(initialModule, initialSubmodule);

    // Handle browser back/forward navigation
    window.addEventListener("popstate", e => {
        if (e.state?.module) {
            loadModule(e.state.module, e.state.submodule);
        }
    });
});
