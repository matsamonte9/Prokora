console.log("User Management JS Loaded!");

document.addEventListener("DOMContentLoaded", function () {
    console.log("User Management module initialized.");

    window.switchToPermissionsView = function () {
        const userView = document.getElementById("user-management-view");
        const permissionsView = document.getElementById("permissions-view");

        if (!userView || !permissionsView) {
            console.error("❌ One of the views is missing in the DOM!");
            return;
        }

        userView.style.display = "none";
        permissionsView.style.display = "block";
        permissionsView.scrollIntoView({ behavior: "smooth" });
        handleModifyPermissions();
    };

    window.switchToUserManagementView = function () {
        const userView = document.getElementById("user-management-view");
        const permissionsView = document.getElementById("permissions-view");

        if (!userView || !permissionsView) {
            console.error("❌ One of the views is missing in the DOM!");
            return;
        }

        permissionsView.style.display = "none";
        userView.style.display = "block";
        console.log("🔄 Switching to User Management View... calling reloadUserTable()");
        reloadUserTable();
    };

    document.addEventListener("submit", async function (e) {
        if (e.target.classList.contains("edit-user-form")) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const userId = formData.get("user-id")?.trim();
            if (!userId) return;

            try {
                const response = await fetch(`/edit_user/${userId}`, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                const data = await response.json();
                if (data.status === "success") {
                    document.querySelector("#popup-edit-user").classList.remove("active");
                    data.redirect ? window.location.href = data.redirect : reloadUserTable();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error("❌ Error in editUserForm:", error);
            }
        }
    });

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("btn-edit-user")) {
            handleEditUser.call(event.target);
        }
        if (event.target.classList.contains("btn-delete-user")) {
            const userId = event.target.dataset.userId;
            if (userId) deleteUser(userId);
        }
        if (event.target.classList.contains("modify-permissions")) {
            handleModifyPermissions.call(event.target);
        }
    });

    async function handleEditUser() {
        const userId = this.dataset.userId;
        const modal = document.querySelector("#popup-edit-user");
        const editForm = document.querySelector(".edit-user-form");
        if (!modal || !editForm) return;

        editForm.reset();
        try {
            const response = await fetch(`/get_user/${userId}?_=${Date.now()}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            const userData = await response.json();
            if (!userData || !userData.name || !userData.email) return;

            editForm.querySelector(".user-id").value = userData.id || "";
            editForm.querySelector(".display-user-id").value = userData.id || "";
            editForm.querySelector(".name").value = userData.name || "";
            editForm.querySelector(".email").value = userData.email || "";
            editForm.querySelector(".role").value = userData.role || "";

            requestAnimationFrame(() => modal.classList.add("active"));
        } catch (error) {
            console.error("❌ Error fetching user data:", error);
            alert("An error occurred while fetching user data.");
        }
    }

    async function deleteUser(userId) {
        if (!confirm("Are you sure you want to delete this user?")) return;
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) return;

            const response = await fetch(`/delete_user/${userId}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            data.success ? (data.reload ? location.reload() : reloadUserTable()) : alert(data.message);
        } catch (error) {
            console.error("❌ Error deleting user:", error);
            alert("An error occurred while deleting the user.");
        }
    }

    async function handleModifyPermissions() {
        try {
            const response = await fetch("/get_all_roles_permissions");
            const data = await response.json();
            const container = document.getElementById("permissions-container");
            if (!container) return;
            container.innerHTML = "";

            data.roles.forEach(role => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${role.name}</td>`;
                ["add", "delete", "edit", "view"].forEach(type => {
                    const perm = role.permissions.find(p => p.name === type);
                    const td = document.createElement("td");
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.checked = perm?.assigned || false;
                    checkbox.dataset.roleId = role.id;
                    checkbox.dataset.permissionId = perm?.id || "";
                    checkbox.onchange = () => togglePermission(checkbox);
                    td.appendChild(checkbox);
                    row.appendChild(td);
                });
                container.appendChild(row);
            });
        } catch (error) {
            console.error("❌ Error fetching role permissions:", error);
        }
    }

    async function togglePermission(checkbox) {
        const roleId = checkbox.dataset.roleId;
        const permissionId = checkbox.dataset.permissionId;
        const action = checkbox.checked ? "add" : "remove";
        if (!roleId || !permissionId) return;

        try {
            await fetch("/modify_permission", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({ role_id: roleId, permission_id: permissionId, action })
            });
        } catch (error) {
            console.error("❌ Error updating permission:", error);
        }
    }

    window.togglePermissionsSection = function () {
        const section = document.getElementById("modify-permissions-section");
        if (!section) return;
        section.style.display = section.style.display === "none" ? "block" : "none";
        if (section.style.display === "block") section.scrollIntoView({ behavior: "smooth" });
    };

    reloadUserTable();
});

function getCurrentUserPage() {
  const match = document.querySelector("#pageInfo")?.textContent.match(/\d+/);
  return parseInt(match?.[0] || 1);
}

function getTotalUserPages() {
  const match = document.querySelector("#pageInfo")?.textContent.match(/\d+$/);
  return parseInt(match?.[0] || 1);
}

function getCurrentSubmodule() {
  const params = new URLSearchParams(window.location.search);
  return params.get("submodule") || "user_list";
}

function changeUserPage(step) {
  const currentPage = getCurrentUserPage();
  const totalPages = getTotalUserPages();
  const newPage = Math.min(Math.max(1, currentPage + step), totalPages);
  const module = "user_management";
  const submodule = getCurrentSubmodule();
  const newUrl = `?module=${module}&submodule=${submodule}&page=${newPage}`;
  history.pushState({}, "", newUrl);
  reloadUserTable(newPage);
}

function userPaginationHandler(e) {
  if (e.target.id === "prevPage") changeUserPage(-1);
  if (e.target.id === "nextPage") changeUserPage(1);
}

function attachUserPaginationListeners() {
  document.querySelectorAll("#prevPage, #nextPage").forEach(btn => {
    btn.removeEventListener("click", userPaginationHandler);
    btn.addEventListener("click", userPaginationHandler);
  });
}

async function reloadUserTable(page = 1) {
  const submodule = getCurrentSubmodule();
  try {
    const response = await fetch(`/get_user_table?submodule=${submodule}&page=${page}`, {
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });

    if (!response.ok) throw new Error("Failed to reload user table");

    const html = await response.text();
    const container = document.getElementById("userTableContainer");
    if (container) {
      container.innerHTML = html;
      attachUserPaginationListeners();
    }
  } catch (error) {
    console.error("❌ reloadUserTable error:", error);
  }
}

window.reloadUserTable = reloadUserTable;
