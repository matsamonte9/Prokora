console.log("Project JS Loaded!");
import { getCurrentModuleAndSubmodule, reloadProjectTable, getCurrentPage, loadProjectTable } from './common.js';

document.addEventListener("DOMContentLoaded", () => {
    console.log("Project module initialized.");
    console.log(userPermissions);
    console.log(getCurrentModuleAndSubmodule());
    console.log(reloadProjectTable);  
    console.log(getCurrentPage());
    console.log(loadProjectTable);  
    
    const { module, submodule } = getCurrentModuleAndSubmodule();  // Get the module and submodule from the URL

    const container = document.querySelector("#projectTableContainer");

    if (container) {
        loadProjectTable(module, submodule);  // Load the project table based on the module and submodule
    } else {
        console.warn("Project table container not found.");
    }
    
    
    // 🔹 Global Click Handler (Delegation)
    document.addEventListener("click", (event) => {
        const target = event.target;
        console.log("Click detected on:", target);

        if (target.classList.contains("btn-view")) toggleViewProjectModal(target);
        if (target.classList.contains("btn-edit-project")) toggleEditProjectModal(target);
        if (target.classList.contains("btn-delete-project")) {
            const projectId = target.dataset.projectId;
            if (projectId) deleteProject(projectId);
        }

        // 🔹 Open Add Modal
        if (target.classList.contains("add-project")) {
            const modal = document.querySelector("#popup-add-project");
            if (modal) {
                modal.classList.add("active");
                console.log("✅ Add Project Modal opened.");
            } else {
                console.error("❌ Add Project Modal not found.");
            }
        }

        // 🔹 Close Add Modal on outside click
        const addModal = document.getElementById("popup-add-project");
        if (addModal?.classList.contains("active") && !addModal.contains(target) && !target.classList.contains("add-project")) {
            addModal.classList.remove("active");
            console.log("🛑 Click outside modal detected, closing Add Project modal.");
        }
    });
    
    // 🔹 Add Project Form Submit
    document.addEventListener("submit", async (e) => {
        if (!e.target.classList.contains("add-project-form")) return;

        e.preventDefault();
        console.log("✅ Add Project Form Submission Detected!");

        const formData = new FormData(e.target);
        const name = formData.get("name")?.trim();
        const desc = formData.get("description")?.trim();
        const status = formData.get("status")?.trim();

        if (!name || !desc || !status) {
            alert("Error: All fields are required.");
            return;
        }

        try {
            const res = await fetch("/projects/add", {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });

            const data = await res.json();
            if (!res.ok || !data.success) throw new Error(data.message);

            console.log("✅ Project added:", data);
            document.getElementById("popup-add-project").classList.remove("active");

            const { module, submodule } = getCurrentModuleAndSubmodule();
            reloadProjectTable(module, submodule);
        } catch (err) {
            console.error("❌ Add Project Error:", err.message);
            alert(err.message);
        }
    });

    // 🔹 Edit Project Form Submit
    document.addEventListener("submit", async (e) => {
        if (!e.target.classList.contains("edit-project-form")) return;

        e.preventDefault();
        console.log("✅ Edit Project Form Submission Detected!");

        const formData = new FormData(e.target);
        const id = formData.get("project_id");
        const name = formData.get("name")?.trim();
        const desc = formData.get("description")?.trim();
        const status = formData.get("status")?.trim();

        if (!id || !name || !desc || !status) {
            alert("Error: All fields are required.");
            return;
        }

        try {
            const res = await fetch(`/projects/edit/${id}`, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });

            const data = await res.json();
            if (!res.ok || data.status !== "success") throw new Error(data.message);

            console.log("✅ Project updated:", data);
            document.getElementById("popup-edit-project").classList.remove("active");

            const { module, submodule } = getCurrentModuleAndSubmodule();
            reloadProjectTable(module, submodule);
        } catch (err) {
            console.error("❌ Edit Project Error:", err.message);
            alert(err.message);
        }
    });

    // 🔹 View Project Modal
    function toggleViewProjectModal(button) {
        const id = button.getAttribute("data-project-id");
        if (!id) return console.error("❌ Missing project ID.");

        fetchProjectData(id, "view");
    }

    // 🔹 Edit Project Modal
    function toggleEditProjectModal(button) {
        const id = button.getAttribute("data-project-id");
        if (!id) return console.error("❌ Missing project ID.");

        fetchProjectData(id, "edit");
    }

    // 🔹 Fetch Data for Modals
    async function fetchProjectData(id, mode = "view") {
        try {
            const res = await fetch(`/projects/view/${id}?_=${Date.now()}`);
            if (!res.ok) throw new Error("Failed to fetch data");

            const { project } = await res.json();
            if (!project) throw new Error("Project data missing");

            const modalId = mode === "edit" ? "popup-edit-project" : "popup-view-project";
            const modal = document.getElementById(modalId);
            if (!modal) throw new Error(`Modal '${modalId}' not found`);

            const fields = {
                id: modal.querySelector(mode === "edit" ? "#edit-project-id" : ".display-project-id"),
                name: modal.querySelector(mode === "edit" ? "#edit-project-name" : ".name"),
                desc: modal.querySelector(mode === "edit" ? "#edit-project-description" : ".description"),
                status: modal.querySelector(mode === "edit" ? "#edit-project-status" : "select[name='status']")
            };

            if (!fields.id || !fields.name || !fields.desc || !fields.status) {
                throw new Error("Missing modal input fields");
            }
            
            fields.id.value = project.id;
            fields.name.value = project.name;
            fields.desc.value = project.description;
            fields.status.value = project.status;
            
            modal.classList.add("active");
            console.log(`✅ ${mode} modal populated and opened.`);
        } catch (err) {
            console.error(`❌ ${mode} Modal Error:`, err.message);
        }
    }

    // 🔹 Delete Project
    async function deleteProject(id) {
        if (!confirm("Are you sure you want to delete this project?")) return;
        
        try {
            const res = await fetch(`/delete_project/${id}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                }
            });
            
            const data = await res.json();
            if (!data.success) throw new Error(data.message);
            
            alert(data.message);
            const { module, submodule } = getCurrentModuleAndSubmodule();
            reloadProjectTable(module, submodule);
        } catch (err) {
            console.error("❌ Delete Project Error:", err.message);
            alert(err.message);
        }
    }
    
    // 🔹 Reload Table
    
    
    // 🔹 Get Current Module/Submodule
    

    // 🔹 Get Current Page
   
});
