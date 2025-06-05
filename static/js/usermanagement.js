console.log("User Management JS Loaded!");

document.addEventListener("DOMContentLoaded", function () {
    console.log("User Management module initialized.");

    // 🔹 View switch logic
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
        
        // userView.scrollIntoView({ behavior: "smooth" });
        
        console.log("🔄 Switching to User Management View... calling reloadUserTable()");
        reloadUserTable();
    };
        
    

    // 🔹 Handle Edit User Form Submission via Event Delegation
    document.addEventListener("submit", async function (e) {
        if (e.target.classList.contains("edit-user-form")) {
            e.preventDefault();
            console.log("✅ Edit User Form Submission Detected!");

            const formData = new FormData(e.target);
            console.log("🛠️ Form Data Before Sending:");
            for (const [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }

            const userId = formData.get("user-id")?.trim();
            if (!userId) {
                console.error("❌ Error: User ID is missing!");
                return;
            }

            try {
                const response = await fetch(`/edit_user/${userId}`, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                if (!response.ok) {
                    throw new Error(`HTTP Error! Status: ${response.status}`);
                }

                const data = await response.json();
                console.log("✅ Edit User Response:", data);

                if (data.status === "success") {
                    console.log("✅ User edited successfully, closing modal...");
                    document.querySelector("#popup-edit-user").classList.remove("active");

                    if (data.redirect) {
                        console.log(`🔄 Redirecting to: ${data.redirect}`);
                        window.location.href = data.redirect;
                    } else {
                        console.log("🔄 Reloading user table...");
                        loadUsers();
                    }
                } else {
                    console.error("❌ Edit User Error:", data.message);
                    alert(data.message);
                }
            } catch (error) {
                console.error("❌ Error in editUserForm:", error);
            }
        }
    });

    // 🔹 Attach Global Click Event Listener for Edit & Delete Buttons
    document.addEventListener("click", function (event) {
        console.log("Click detected on:", event.target);

        if (event.target.classList.contains("btn-edit")) {
            handleEditUser.call(event.target);
        }

        if (event.target.classList.contains("btn-delete")) {
            const userId = event.target.dataset.userId;
            if (userId) {
                deleteUser(userId);
            }
        }

        if (event.target.classList.contains("modify-permissions")) {
            handleModifyPermissions.call(event.target);
        }
    });

    function attachModifyPermissionsEventListener() {
        const modifyPermissionsForm = document.querySelector(".modify-permissions-form");
        if (modifyPermissionsForm) {
            modifyPermissionsForm.addEventListener("submit", function (e) {
                e.preventDefault();
                console.log("✅ Modify Permissions Form Submitted!");
            });
        }
    }

    async function handleEditUser() {
        console.log("📌 Edit Button clicked! Checking dataset:", this.dataset);

        const userId = this.dataset.userId;
        if (!userId) {
            console.error("❌ Error: No user ID found in dataset!");
            return;
        }

        console.log(`🔄 Fetching fresh data for user ID: ${userId}`);

        const modal = document.querySelector("#popup-edit-user");
        const editForm = document.querySelector(".edit-user-form");

        if (!modal || !editForm) {
            console.error("❌ ERROR: Edit User Modal or Form not found in the DOM!");
            return;
        }

        editForm.reset();

        try {
            const response = await fetch(`/get_user/${userId}?_=${new Date().getTime()}`, {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (!response.ok) {
                throw new Error(`HTTP Error! Status: ${response.status}`);
            }

            const userData = await response.json();
            console.log("✅ Fresh user data received:", userData);

            if (!userData || !userData.name || !userData.email) {
                console.error("❌ ERROR: Received empty or incorrect user data!", userData);
                alert("Error: User data is incomplete or unavailable.");
                return;
            }

            const userIdField = editForm.querySelector(".user-id");
            const displayUserIdField = editForm.querySelector(".display-user-id");
            const nameField = editForm.querySelector(".name");
            const emailField = editForm.querySelector(".email");
            const roleField = editForm.querySelector(".role");

            if (!userIdField || !displayUserIdField || !nameField || !emailField || !roleField) {
                console.error("❌ ERROR: One or more form fields are missing! Check HTML structure.");
                return;
            }

            userIdField.value = userData.id || "";
            displayUserIdField.value = userData.id || "";
            nameField.value = userData.name || "";
            emailField.value = userData.email || "";
            roleField.value = userData.role || "";

            requestAnimationFrame(() => {
                modal.classList.add("active");
                console.log("✅ Edit User Modal Opened!");
            });

        } catch (error) {
            console.error("❌ Error fetching user data:", error);
            alert("An error occurred while fetching user data.");
        }
    }

    function updateUserRow(userId, updatedData) {
        const row = document.querySelector(`tr[data-user-id='${userId}']`);
        if (row) {
            row.querySelector(".user-name").textContent = updatedData.name;
            row.querySelector(".user-email").textContent = updatedData.email;
            row.querySelector(".user-role").textContent = updatedData.role;
            console.log("✅ User row updated successfully.");
        }
    }

    async function handleModifyPermissions() {
        console.log("✅ Modify Permissions button clicked!");

        try {
            const response = await fetch("/get_all_roles_permissions");
            if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);

            const data = await response.json();
            console.log("✅ Retrieved Roles and Permissions Data:", data);

            const permissionsContainer = document.getElementById("permissions-container");
            if (!permissionsContainer) {
                console.error("❌ ERROR: permissions-container not found!");
                return;
            }

            permissionsContainer.innerHTML = "";

            data.roles.forEach(role => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${role.name}</td>`;

                ["add", "delete", "edit", "view"].forEach(permissionType => {
                    const permission = role.permissions.find(p => p.name === permissionType);
                    const isChecked = permission ? permission.assigned : false;
                    const permissionId = permission ? permission.id : "";

                    const td = document.createElement("td");
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.name = `permissions_${role.id}_${permissionType}`;
                    checkbox.dataset.roleId = role.id;
                    checkbox.dataset.permissionId = permissionId;
                    checkbox.onchange = function () {
                        togglePermission(this);
                    };

                    checkbox.checked = isChecked;
                    if (isChecked) {
                        checkbox.setAttribute("checked", "checked");
                    }

                    td.appendChild(checkbox);
                    row.appendChild(td);
                });

                permissionsContainer.appendChild(row);
            });
        } catch (error) {
            console.error("❌ Error fetching role permissions:", error);
        }
    }
    
    async function togglePermission(checkbox) {
        const roleId = checkbox.dataset.roleId;
        const permissionId = checkbox.dataset.permissionId;
        const action = checkbox.checked ? "add" : "remove";

        if (!roleId || !permissionId) {
            console.error("❌ ERROR: Missing role or permission ID!");
            return;
        }

        console.log(`🔄 Updating Permission: Role ${roleId}, Permission ${permissionId}, Action: ${action}`);

        try {
            const response = await fetch("/modify_permission", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({ role_id: roleId, permission_id: permissionId, action: action })
            });

            const result = await response.json();
            console.log("✅ Permission update response:", result);
        } catch (error) {
            console.error("❌ Error updating permission:", error);
        }
    }

    function getCsrfToken() {
        const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfTokenMeta ? csrfTokenMeta.getAttribute("content") : null;
    }

    async function deleteUser(userId) {
        const isConfirmed = confirm("Are you sure you want to delete this user?");
        if (!isConfirmed) {
            console.log("❌ User deletion canceled.");
            return;
        }

        try {
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                console.error("❌ CSRF token is missing!");
                return;
            }

            const response = await fetch(`/delete_user/${userId}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();

            if (data.success) {
                alert(data.message);

                if (data.reload) {
                    location.reload();
                } else {
                    reloadUserTable();
                }
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error("❌ Error deleting user:", error);
            alert("An error occurred while deleting the user.");
        }
    }

    async function reloadUserTable() {
        try {
            const response = await fetch("/get_user_table", {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (!response.ok) throw new Error("Failed to reload user table");

            const html = await response.text();
            const userTableContainer = document.getElementById("userTableContainer");
            if (userTableContainer) {
                userTableContainer.innerHTML = html;
                console.log("✅ User table reloaded successfully.");
            } else {
                console.error("❌ User Table container not found in the DOM!");
            }
        } catch (error) {
            console.error("❌ Error reloading user table:", error);
        }
    }

    // 🔹 Global toggle function for use in HTML onclick
    window.togglePermissionsSection = function () {
        const section = document.getElementById("modify-permissions-section");
        if (!section) {
            console.error("Permissions section not found.");
            return;
        }
        
        const isHidden = section.style.display === "none" || section.style.display === "";
        section.style.display = isHidden ? "block" : "none";
        
        if (isHidden) {
            section.scrollIntoView({ behavior: "smooth" });
        }
    };
});
