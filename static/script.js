console.log("Hi");

const remove_selected_image = (event) => {
  event.preventDefault();
  event.stopPropagation();
  const image_input = document.querySelector("#tweet_image");
  image_input.value = "";
  const image_name_display = document.querySelector("#image_name");
  if (image_input.value === "") {
    image_name_display.textContent = "No image";
    document
      .querySelector("label[for='tweet_image']")
      .classList.remove("hidden");
    document.querySelector("#remove_image").classList.add("hidden");
  }
};

const tweet_image_changed = (event) => {
  const image_filename = event.target.value.slice(
    event.target.value.lastIndexOf("\\") + 1
  );
  const image_name_display = document.querySelector("#image_name");
  if (image_filename !== "" && image_filename !== undefined) {
    image_name_display.textContent = image_filename;
    document.querySelector("label[for='tweet_image']").classList.add("hidden");
    document.querySelector("#remove_image").classList.remove("hidden");
  } else {
    image_name_display.textContent = "No image";
  }
};

const display_login_modal = async (event) => {
  console.log("log in now");
  console.log(event);
  response = await fetch("/login", {
    method: "GET",
  })
    .then((response) => {
      // check response
      if (!response.ok) {
        window.location = "/";
        return;
      }
      return response.text();
    })
    .then((responseText) => {
      // get the html content from the response text
      const content = responseText.slice(
        responseText.indexOf('<html lang="en">') + '<html lang="en">'.length,
        responseText.indexOf("</html>")
      );
      console.log(responseText);
      console.log(content);

      // set the html to the content
      document.querySelector("html").innerHTML = content;

      // update url (with errors in query string or whatever page it's been redirected to)
      window.history.pushState(null, null, "/login");
    });
};

const display_signup_modal = (event) => {
  console.log("sign up now");
  console.log(event);
};

const logout = async (event) => {
  await fetch("/logout", {
    method: "PUT",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    window.location.href = "/";
  });
};

const delete_tweet = async (event) => {
  tweet_id = event.target.id.slice(2);
  await fetch("/tweets/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    window.location.href = "/home";
  });
};

const open_profile = (event) => {
  console.log("click on profile");
};
