// Get current module and submodule from the URL
export function getCurrentModuleAndSubmodule() {
    const params = new URLSearchParams(window.location.search);
    return {
        module: params.get("module") || "projects",
        submodule: params.get("submodule") || "ongoing"
    };
}

// Get the current page from the URL (default to 1)
export function getCurrentPage() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('page')) || 1; // Default to page 1 if no page param
}

// Re-attach event listeners for buttons (view/edit/delete)
function attachProjectButtonListeners() {
    document.querySelectorAll(".btn-view").forEach(btn => {
        btn.onclick = () => toggleViewProjectModal(btn);
    });

    document.querySelectorAll(".btn-edit-project").forEach(btn => {
        btn.onclick = () => toggleEditProjectModal(btn);
    });

    document.querySelectorAll(".btn-delete-project").forEach(btn => {
        btn.onclick = () => {
            const id = btn.dataset.projectId;
            deleteProject(id);
        };
    });
}

// Attach pagination button event listeners
function attachPaginationListeners() {
    document.querySelectorAll("#prevPage, #nextPage").forEach(btn => {
        btn.removeEventListener("click", paginationHandler); // Prevent duplicates
        btn.addEventListener("click", paginationHandler);
    });
}

// Pagination click handler
function paginationHandler(e) {
    if (e.target.id === "prevPage") {
        changePage(-1);
    } else if (e.target.id === "nextPage") {
        changePage(1);
    }
}

// Change the page and reload table with updated query param
function changePage(step) {
    const currentPage = getCurrentPage();
    const totalPages = parseInt(document.querySelector('#pageInfo')?.textContent.match(/\d+$/)?.[0]) || 1;
    const newPage = Math.min(Math.max(1, currentPage + step), totalPages);

    const { module, submodule } = getCurrentModuleAndSubmodule();
    const newUrl = `?module=${module}&submodule=${submodule}&page=${newPage}`;
    window.history.pushState({}, '', newUrl);
    reloadProjectTable(module, submodule);
}

// Reload the table dynamically
export function reloadProjectTable(module, submodule) {
    if (!module) module = "projects";
    if (!submodule) submodule = "ongoing";

    const currentPage = getCurrentPage();

    fetch(`/get_project_table?module=${module}&submodule=${submodule}&page=${currentPage}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.text())
    .then(html => {
        const container = document.querySelector("#projectTableContainer");
        if (container) {
            container.innerHTML = html;
            attachProjectButtonListeners();
            attachPaginationListeners(); // ✅ Important fix
        }
    })
    .catch(err => console.error("Failed to reload project table:", err));
}

// Reusable load for project table with explicit page
export function loadProjectTable(module, submodule = "ongoing", page = 1) {
    const url = `/get_project_table?module=${module}&submodule=${submodule}&page=${page}`;
    history.pushState({}, "", `?module=${module}&submodule=${submodule}&page=${page}`);
    
    fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.text())
    .then(html => {
        const container = document.querySelector("#projectTableContainer");
        if (container) {
            container.innerHTML = html;
            attachProjectButtonListeners();
            attachPaginationListeners(); // ✅ Important fix
        } else {
            console.warn("Project table container not found.");
        }
    })
    .catch(err => console.error("Failed to load project table:", err));
}

// On page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const { module, submodule } = getCurrentModuleAndSubmodule();
        reloadProjectTable(module, submodule);
    }, 100); // wait 100ms

    console.log("Common JS Loaded!");

    const container = document.querySelector("#projectTableContainer");
    const { module, submodule } = getCurrentModuleAndSubmodule();

    reloadProjectTable(module, submodule);

    if (container) {
        if (submodule === "ongoing" || submodule === "finished") {
            reloadProjectTable(module, submodule);
        } else {
            console.warn("Invalid submodule for table reload. Skipping...");
        }
    } else {
        console.warn("Project table container not found.");
    }

    // ❌ REMOVE this old delegation — it's now handled dynamically
    // document.addEventListener("click", (e) => {
    //     if (e.target.id === "prevPage") {
    //         changePage(-1);
    //     } else if (e.target.id === "nextPage") {
    //         changePage(1);
    //     }
    // });
});
