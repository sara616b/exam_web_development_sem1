////////////////////////////////////////////////////////////////
// The first time the page loads set title and state
window.addEventListener("DOMContentLoaded", () => {
  const mainContent = document.querySelector(".content");

  // set title
  const title = mainContent.dataset.title;
  document.title = title;

  // Set the state for the first loaded page
  const url = mainContent.dataset.url;
  history.replaceState({ url: url }, "", url);
});

////////////////////////////////////////////////////////////////
// spa - fetch and show content
const spa = async (url, replace_state = true, event) => {
  event.preventDefault();
  event.stopPropagation();

  // Check if page is already loaded
  // Fetch the html content
  let conn = await fetch(url, { headers: { spa: "yes" } });
  let html = await conn.text();

  // set the html to the content
  document.querySelector("body").innerHTML = html;

  // set title
  const mainContent = document.querySelector(".content");
  const title = mainContent.dataset.title;
  document.title = title;

  // set state
  if (replace_state || conn.url !== url) {
    history.pushState({ url: conn.url }, "", conn.url);
  }
};

////////////////////////////////////////////////////////////////
// handle clicking 'back' in the browsers
window.addEventListener("popstate", (event) => {
  spa(event.state.url, false, event);
  return false;
});
