// Enhanced JavaScript for Blue & White Theme
document.addEventListener("DOMContentLoaded", function () {
  initializeTheme();
  initializeTooltips();
  initializeDownloadButtons();
  initializeAnimations();
});

function initializeTheme() {
  // Add theme-specific classes
  document.querySelectorAll(".btn-primary").forEach((btn) => {
    btn.classList.add("shadow-sm");
  });

  document.querySelectorAll(".card").forEach((card) => {
    card.classList.add("shadow-sm");
  });
}

function initializeTooltips() {
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

function initializeDownloadButtons() {
  document.querySelectorAll(".download-btn").forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const downloadType = this.dataset.type;
      const url = this.dataset.url;
      const username = this.dataset.username;
      const id = this.dataset.id;

      downloadMedia(downloadType, url, username, id);
    });
  });
}

function initializeAnimations() {
  // Add intersection observer for fade-in animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe cards for animation
  document.querySelectorAll(".card").forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(card);
  });
}

function downloadMedia(type, url, username, id) {
  const button = event.target.closest(".download-btn");
  const originalText = button.innerHTML;
  const originalClass = button.className;

  // Show loading state with blue theme
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
  button.className = originalClass + " disabled";
  button.disabled = true;

  let endpoint = "";
  let data = {};

  switch (type) {
    case "story":
      endpoint = "/download/story";
      data = { url, username, story_id: id };
      break;
    case "post":
      endpoint = "/download/post";
      data = { post_data: JSON.parse(decodeURIComponent(url)), username };
      break;
    case "profile_pic":
      endpoint = "/download/profile-pic";
      data = { profile_data: JSON.parse(decodeURIComponent(url)) };
      break;
  }

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.success) {
        showAlert("Download completed successfully!", "success");

        // Trigger actual file download
        if (result.filepath) {
          const link = document.createElement("a");
          link.href = "/" + result.filepath;
          link.download = result.filename;
          link.style.display = "none";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      } else {
        showAlert(
          "Download failed: " + (result.error || "Unknown error"),
          "danger"
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showAlert("Download failed: Network error", "danger");
    })
    .finally(() => {
      // Restore button state with smooth transition
      setTimeout(() => {
        button.innerHTML = originalText;
        button.className = originalClass;
        button.disabled = false;
      }, 1000);
    });
}

function showAlert(message, type) {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow-sm`;
  alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  const container = document.querySelector("main .container");
  container.insertBefore(alertDiv, container.firstChild);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentElement) {
      alertDiv.remove();
    }
  }, 5000);
}

function getAlertIcon(type) {
  const icons = {
    success: "check-circle",
    danger: "exclamation-triangle",
    warning: "exclamation-circle",
    info: "info-circle",
  };
  return icons[type] || "info-circle";
}

// Utility functions with blue theme enhancements
function formatNumber(num) {
  if (!num) return "0";
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

// Enhanced file operations
function downloadAllStories() {
  const downloadButtons = document.querySelectorAll(
    '.download-btn[data-type="story"]'
  );
  startBatchDownload(downloadButtons, "stories");
}

function downloadAllPosts() {
  const downloadButtons = document.querySelectorAll(
    '.download-btn[data-type="post"]'
  );
  startBatchDownload(downloadButtons, "posts");
}

function startBatchDownload(buttons, type) {
  let downloaded = 0;
  const total = buttons.length;

  if (total === 0) {
    showAlert(`No ${type} available to download.`, "warning");
    return;
  }

  showAlert(`Starting batch download of ${total} ${type}...`, "info");

  buttons.forEach((button, index) => {
    setTimeout(() => {
      button.click();
      downloaded++;

      // Update progress
      if (downloaded % 5 === 0 || downloaded === total) {
        showAlert(`Downloaded ${downloaded} of ${total} ${type}...`, "info");
      }

      if (downloaded === total) {
        setTimeout(() => {
          showAlert(`All ${type} download completed!`, "success");
        }, 2000);
      }
    }, index * 1500); // 1.5 second delay between downloads
  });
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});
