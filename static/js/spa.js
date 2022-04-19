////////////////////////////////////////////////////////////////
// The first time the page loads set title and state
window.addEventListener("DOMContentLoaded", () => {
  const mainContent = document.querySelector(".content");

  // Set the state for the first loaded page
  const url = mainContent.dataset.url;
  history.replaceState({ url: url }, "", url);

  // set title
  const title = mainContent.dataset.title;
  document.title = title;
});

////////////////////////////////////////////////////////////////
// spa - fetch and show content
const spa = async (url, replace_state = true, event = null) => {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  // Check if page is already loaded
  // Fetch the html content
  let conn = await fetch(url, { headers: { spa: "yes" } });
  let html = await conn.text();

  // set the html to the content
  document.querySelector("body").innerHTML = html;

  // set state
  if (replace_state) {
    history.pushState({ url: conn.url }, "", conn.url);
    // scroll to top of page
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  } else {
    // if the connection has been redirected, call spa again to update to correct page
    // this happens when clicking the backbutton and landing on '/login' which, while logged in, will redirect to '/home'
    if (conn.redirected) {
      spa(conn.url, true);
    }
  }

  // set title
  const mainContent = document.querySelector(".content");
  const title = mainContent.dataset.title;
  document.title = title;
};

////////////////////////////////////////////////////////////////
// handle clicking 'back' in the browsers
window.addEventListener("popstate", (event) => {
  spa(event.state.url, false, event);
  return false;
});
