document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.querySelector("[data-theme-toggle]");
  const updateThemeToggle = () => {
    if (!themeToggle) return;
    const isDark = document.documentElement.dataset.theme === "dark";
    themeToggle.setAttribute("aria-pressed", String(isDark));
    themeToggle.setAttribute("aria-label", `Switch to ${isDark ? "light" : "dark"} mode`);
    themeToggle.querySelector("[data-theme-icon]").textContent = isDark ? "☀" : "☾";
    themeToggle.querySelector(".theme-toggle-label").textContent = isDark ? "Light mode" : "Dark mode";
  };
  updateThemeToggle();
  themeToggle?.addEventListener("click", () => {
    const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("blogsphere-theme", theme);
    } catch {
      // The selected theme remains active for the current page if storage is unavailable.
    }
    updateThemeToggle();
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
});

window.initializeEditor = (initialHtml, uploadUrl, csrfToken) => {
  const editorElement = document.querySelector("#rich-editor");
  const source = document.querySelector("#content-source");
  const form = editorElement?.closest("form");
  const imageInput = document.querySelector("#inline-image-input");
  const uploadStatus = document.querySelector("#image-upload-status");
  if (!editorElement || !source || !window.Quill) return;

  const toolbar = document.querySelector("#editor-toolbar");
  const editor = new Quill(editorElement, {
    theme: "snow",
    modules: {
      toolbar: {
        container: "#editor-toolbar",
        handlers: {
          image() {
            imageInput?.click();
          },
        },
      },
    },
    placeholder: "Start with a thought...",
  });
  if (initialHtml) editor.setContents(editor.clipboard.convert({ html: initialHtml }));
  source.hidden = true;
  source.removeAttribute("required");
  source.removeAttribute("minlength");
  editorElement.hidden = false;
  editorElement.setAttribute("role", "textbox");
  editorElement.setAttribute("aria-multiline", "true");
  editorElement.setAttribute("aria-labelledby", "article-content-label");
  toolbar.hidden = false;
  document.querySelector("#article-content-label").removeAttribute("for");
  source.form.addEventListener("submit", () => {
    source.value = editor.root.innerHTML;
  });
  imageInput?.addEventListener("change", async () => {
    const image = imageInput.files?.[0];
    if (!image) return;
    uploadStatus.textContent = "Uploading image…";
    const data = new FormData();
    data.append("image", image);
    try {
      const response = await fetch(uploadUrl, {
        method: "POST",
        body: data,
        headers: { "X-CSRFToken": csrfToken },
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Image upload failed.");
      const selection = editor.getSelection(true);
      editor.insertEmbed(selection.index, "image", result.url, "user");
      editor.setSelection(selection.index + 1);
      uploadStatus.textContent = "Image added to your article.";
    } catch (error) {
      uploadStatus.textContent = error.message || "Image upload failed. Try again.";
    } finally {
      imageInput.value = "";
    }
  });
};
