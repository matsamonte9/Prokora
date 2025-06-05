document.addEventListener("DOMContentLoaded", function () {
  const profilePhotoId = "profile-photo";

  function toggleProfileMenu() {
    const profileMenu = document.getElementById("profile-menu");
    const profilePhoto = document.getElementById(profilePhotoId);
    if (!profileMenu || !profilePhoto) return;

    if (profileMenu.classList.contains("show")) {
      profileMenu.classList.remove("show");
      profilePhoto.setAttribute("aria-expanded", "false");
    } else {
      profileMenu.classList.add("show");
      profilePhoto.setAttribute("aria-expanded", "true");
      profileMenu.focus();
    }
  }

  let toggleInProgress = false;

  document.addEventListener("click", function (e) {
    const profileMenu = document.getElementById("profile-menu");
    const profilePhoto = document.getElementById(profilePhotoId);
    const profileContainer = document.querySelector(".profile-menu-container");

    if (e.target.closest(`#${profilePhotoId}`)) {
      e.stopPropagation();
      if (toggleInProgress) return;
      toggleInProgress = true;
      toggleProfileMenu();
      setTimeout(() => { toggleInProgress = false; }, 0);
    } else {
      if (profileMenu && profileMenu.classList.contains("show") &&
          (!profileContainer || !profileContainer.contains(e.target))) {
        profileMenu.classList.remove("show");
        if (profilePhoto) profilePhoto.setAttribute("aria-expanded", "false");
      }
    }
  });

  document.addEventListener("keydown", function (e) {
    const focused = document.activeElement;
    const profileMenu = document.getElementById("profile-menu");
    const profilePhoto = document.getElementById(profilePhotoId);

    if (focused && focused.id === profilePhotoId) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleProfileMenu();
      }
    }

    if (e.key === "Escape" && profileMenu && profileMenu.classList.contains("show")) {
      profileMenu.classList.remove("show");
      if (profilePhoto) {
        profilePhoto.setAttribute("aria-expanded", "false");
        profilePhoto.focus();
      }
    }
  });

  document.addEventListener("click", function (e) {
    const profileMenu = document.getElementById("profile-menu");
    if (profileMenu && profileMenu.contains(e.target)) {
      e.stopPropagation();
    }
  });

  window.openEditUserProfileModal = function (anchor) {
    const profileMenu = document.getElementById("profile-menu");
    const profilePhoto = document.getElementById(profilePhotoId);

    if (profileMenu && profileMenu.classList.contains("show")) {
      profileMenu.classList.remove("show");
      if (profilePhoto) profilePhoto.setAttribute("aria-expanded", "false");
    }
    toggleEditUserProfileModal(anchor);
  };

  function toggleEditUserProfileModal(anchor) {
    if (!anchor) return console.error("No anchor element provided");
    const userId = anchor.getAttribute("data-user-id");
    const modal = document.getElementById("popup-edit-user-profile");
    if (!modal) return console.error("Modal not found!");

    fetchUserData(userId)
      .then(() => modal.classList.add("active"))
      .catch((error) => console.error("Fetch error:", error));
  }

  async function fetchUserData(userId) {
    try {
      const response = await fetch(`/user/view/${userId}?_=${Date.now()}`);
      if (!response.ok) throw new Error("Failed to fetch user data");
      const userData = await response.json();
      const modal = document.getElementById("popup-edit-user-profile");

      modal.querySelector("#edit-user-profile-id").value = userData.user.id;
      modal.querySelector(".display-user-id").value = userData.user.id;
      modal.querySelector("#edit-user-profile-name").value = userData.user.name;
      modal.querySelector("#edit-user-profile-email").value = userData.user.email;
      modal.querySelector("#edit-user-profile-role").value = userData.user.role;
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  }
});

document.addEventListener("submit", async function (e) {
  if (e.target.classList.contains("edit-user-profile-form")) {
    e.preventDefault();
    const formData = new FormData(e.target);

    const userId = formData.get("user_id")?.trim();
    if (!userId) {
      console.error("User ID is missing!");
      return;
    }

    try {
      const response = await fetch(`/user/edit_profile/${userId}`, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);

      const data = await response.json();
      if (data.status === "success") {
        document.querySelector("#popup-edit-user-profile").classList.remove("active");
        // Instead of reloading the page, update the displayed username dynamically:
        const userNameDisplay = document.querySelector(".user--info .info b");
        const updatedName = formData.get("name");
        if (userNameDisplay && updatedName) {
          userNameDisplay.textContent = updatedName;
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error("Error in editUserProfileForm:", error);
    }
  }
});
