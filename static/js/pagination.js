const rowsPerPage = 5;
window.currentPage = 1;

// Initialize pagination on DOMContentLoaded and after AJAX table reload
function initializePagination() {
    document.addEventListener("DOMContentLoaded", setupPagination);

    // Optional: expose this globally so you can call after dynamic reload
    window.setupPagination = setupPagination;
}

function setupPagination() {
    const paginationContainer = document.getElementById("pagination-controls");

    if (!paginationContainer) {
        console.warn("Pagination container not found.");
        return;
    }

    // Re-attach event listeners every time (safe approach)
    const prevButton = document.getElementById("prevPage");
    const nextButton = document.getElementById("nextPage");

    if (prevButton) {
        prevButton.onclick = () => changePage(-1);
    }
    if (nextButton) {
        nextButton.onclick = () => changePage(1);
    }

    paginateProjects();  // Always run pagination logic
}

function paginateProjects() {
    const rows = document.querySelectorAll("tbody tr");
    const totalPages = Math.max(1, Math.ceil(rows.length / rowsPerPage));

    // Clamp currentPage if needed
    window.currentPage = Math.min(window.currentPage, totalPages);

    rows.forEach((row, index) => {
        row.style.display =
            index >= (window.currentPage - 1) * rowsPerPage &&
            index < window.currentPage * rowsPerPage
                ? ""
                : "none";
    });

    updatePaginationControls(totalPages);
}

function updatePaginationControls(totalPages) {
    const pageInfo = document.getElementById("pageInfo");
    const prevButton = document.getElementById("prevPage");
    const nextButton = document.getElementById("nextPage");

    if (pageInfo) {
        pageInfo.textContent = `Page ${window.currentPage} of ${totalPages}`;
    }

    if (prevButton) {
        prevButton.disabled = window.currentPage === 1;
    }

    if (nextButton) {
        nextButton.disabled = window.currentPage === totalPages;
    }
}

function changePage(step) {
    const rows = document.querySelectorAll("tbody tr");
    if (rows.length === 0) return;

    const totalPages = Math.ceil(rows.length / rowsPerPage);
    window.currentPage = Math.max(1, Math.min(window.currentPage + step, totalPages));
    
    const { module, submodule } = getCurrentModuleAndSubmodule();
    const newUrl = `?module=${module}&submodule=${submodule}&page=${window.currentPage}`;
    window.history.pushState({}, '', newUrl);

    reloadProjectTable(module, submodule);
}

// Initialize on load
initializePagination();
