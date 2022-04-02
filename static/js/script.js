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

const log_out = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  await fetch("/logout", {
    method: "PUT",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // get to frontpage
    spa("/", true, event);
  });
};

const delete_tweet = async (event) => {
  const tweet_id = event.target.id.slice(2);
  await fetch("/tweets/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    spa("/home", true, event);
  });
};

const like_tweet = async (event) => {
  tweet_id = event.target.id.slice(4);
  if (!event.target.classList.contains("likedTrue")) {
    await fetch("/tweets/like/" + tweet_id, {
      method: "POST",
    }).then((response) => {
      if (!response.ok) {
        return;
      }
    });
  } else {
    await fetch("/tweets/like/" + tweet_id, {
      method: "DELETE",
    }).then((response) => {
      if (!response.ok) {
        return;
      }
    });
  }
  // get home feed
  spa("/home", true, event);
};

const open_profile = (event) => {
  console.log("click on profile");
};

const post_new_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  const form = event.target.form;
  await fetch("/tweets/new", {
    method: "POST",
    body: new FormData(form),
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // get home feed
    spa("/home", true, event);
  });
};

const put_edited_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  console.log(event);
  const form = event.target.form;
  const tweet_id = event.target.id.slice(2);
  await fetch("/tweets/" + tweet_id, {
    method: "PUT",
    body: new FormData(form),
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // get home feed
    spa("/home", true, event);
  });
};

const sign_up = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  const form = event.target.form;
  const is_valid = validate(form);
  console.log("is_valid", is_valid);
  if (is_valid) {
    await fetch("/signup", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      // get to login
      spa("/login", true, event);
    });
  }
};

const log_in = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  const form = event.target.form;
  const is_valid = validate(form);
  console.log("is_valid", is_valid);
  if (is_valid) {
    await fetch("/login", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      // get to home feed
      spa("/home", true, event);
    });
  }
};
