function toggleAddUserModal() {
    const modal = document.getElementById("popup-add-user");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Add User Modal not found!");
    }
}

function toggleEditUserModal() {
    const modal = document.getElementById("popup-edit-user");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Edit User Modal not found!");
    }
}

function toggleModifyPermissionsModal() {
    const modal = document.getElementById("modify-permissions-modal");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Modify Permissions Modal not found!");
    }
}

function closeModifyPermissionsModal() {
    const modal = document.getElementById("modify-permissions-modal");
    if (modal) {
        modal.classList.remove("active");
    } else {
        console.error("Modify Permissions Modal not found!");
    }
}

function toggleAddProjectModal() {
    const modal = document.getElementById("popup-add-project");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Add Project Modal not found!");
    }
}

function toggleEditProjectModal() {
    const modal = document.getElementById("popup-edit-project");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Edit Project Modal not found!");
    }
}

function toggleViewProjectModal() {
    const modal = document.getElementById("popup-view-project");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("View Project Modal not found!");
    }
}

function toggleEditUserProfileModal() {
    const modal = document.getElementById("popup-edit-user-profile");
    if (modal) {
        modal.classList.toggle("active");
    } else {
        console.error("Edit User Profile not found!");
    }
}