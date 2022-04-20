const sign_up = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.value;
  event.target.value = "signing up...";
  const form = event.target.form;
  // const is_valid = true;
  const is_valid = validate(form);
  if (is_valid) {
    await fetch("/signup", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get to login
        spa("/login", true, event);
      }
    });
  }
  // remove elipses
  event.target.value = submit_button_value;
};

const log_in = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.value;
  event.target.value = "logging in...";

  const form = event.target.form;
  const is_valid = validate(form);
  // const is_valid = true;
  if (is_valid) {
    await fetch("/login", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get to home feed
        spa("/home", true, event);
      }
    });
  }
  // remove elipses
  event.target.value = submit_button_value;
};

const log_out = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "logging out...";
  event.target.classList.add("disabled");
  await fetch("/logout", {
    method: "PUT",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // get to frontpage
    spa("/", true, event);
  });
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const post_new_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "posting...";
  event.target.classList.add("disabled");
  const form = event.target.form;
  const is_valid = validate(form);
  if (is_valid) {
    await fetch("/tweets/new", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected && response.url != window.location.href) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get home feed
        spa("/home", true, event);
      }
    });
  }
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const put_edited_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "posting...";
  event.target.classList.add("disabled");
  const form = event.target.form;
  const tweet_id = event.target.id.slice(2);
  const is_valid = validate(form);
  if (is_valid) {
    await fetch("/tweets/" + tweet_id, {
      method: "PUT",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get home feed
        spa("/home", true, event);
      }
    });
  }
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const delete_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "deleting...";
  event.target.classList.add("disabled");
  const tweet_id = event.target.id.slice(2);
  await fetch("/tweets/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      event.target.textContent = submit_button_value;
      spa(response.url, false, event);
      event.target.classList.remove("disabled");
      return;
    }
    // delete tweet from ui (could be done with spa, but this saves a get request)
    const tweets = document.querySelectorAll(
      ".tweet_container[data-id='id" + tweet_id + "']"
    );
    tweets.forEach((tweet) => {
      tweet.remove();
    });

    // delete tweet from ui (could be done with spa, but this saves a get request)
    const retweets = document.querySelectorAll(
      ".retweet_container[data-tweet-id='id" + tweet_id + "']"
    );
    retweets.forEach((retweet) => {
      retweet.remove();
    });
    // spa(window.location.pathname, false, event);
  });
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const retweet_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  const tweet_id = event.target.dataset.tweetId.slice(2);
  // if (event.target.dataset.twee == "False") {
  await fetch("/tweets/retweet/" + tweet_id, {
    method: "POST",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    event.target.nextElementSibling.textContent =
      parseInt(event.target.nextElementSibling.textContent) + 1;

    if (response.redirected && response.url != window.location.href) {
      // if it's been redirected there're errors send with query string
      spa(response.url, true, event);
    } else {
      // get home feed
      spa("/home", true, event);
    }
  });
};

const delete_retweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "deleting...";
  event.target.classList.add("disabled");
  const retweet_id = event.target.dataset.retweetId.slice(2);
  // const tweet_id = event.target.dataset.tweetId.slice(2);
  await fetch("/retweets/delete/" + retweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      event.target.textContent = submit_button_value;
      spa(response.url, false, event);
      event.target.classList.remove("disabled");
      return;
    }
    spa(window.location.pathname, false, event);
  });
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const toggle_like_tweet = async (event) => {
  const tweet_id = event.target.id.slice(4);
  const like_buttons = document.querySelectorAll(
    "[data-tweet-id='id" + tweet_id + "'].like_button"
  );
  const method = event.target.dataset.liked == "False" ? "POST" : "DELETE";
  // if (event.target.dataset.liked == "False") {
  await fetch("/tweets/like/" + tweet_id, {
    method: method,
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // only redirected if there's an error
    if (response.redirected) {
      // redirected url will contain error alert message - don't replace state, stay on page
      spa(response.url, false);
      return;
    }
    like_buttons.forEach((button) => {
      if (event.target.dataset.liked == "False") {
        button.nextElementSibling.textContent =
          parseInt(button.nextElementSibling.textContent) + 1;
      } else {
        button.nextElementSibling.textContent =
          parseInt(button.nextElementSibling.textContent) - 1;
      }
    });
  });
  // update ui (could be done with spa, but save the request)
  like_buttons.forEach((button) => {
    button.dataset.liked = button.dataset.liked == "True" ? "False" : "True";
  });
  // spa(window.location.pathname, false, event);
};

const view_user = async (event) => {
  const username = event.target.dataset.username.slice(2);
  await fetch("/users/" + username, {
    method: "GET",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      spa(response.url, true, event);
      return;
    }
    spa("/users/" + username, true, event);
  });
};

const follow_user = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent =
    event.target.dataset.follows == "False" ? "following..." : "unfollowing...";
  event.target.classList.add("disabled");
  const user_id_to_follow = event.target.dataset.userid.slice(2);
  if (event.target.dataset.follows == "False") {
    await fetch("/users/follow/" + user_id_to_follow, {
      method: "POST",
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        event.target.textContent = submit_button_value;
        spa(response.url, true, event);
        event.target.classList.remove("disabled");
        return;
      }
    });
  } else {
    await fetch("/users/follow/" + user_id_to_follow, {
      method: "DELETE",
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        event.target.textContent = submit_button_value;
        spa(response.url, true, event);
        event.target.classList.remove("disabled");
        return;
      }
    });
  }

  // update the ui (could be done with spa, but save the request)
  const follow_buttons = document.querySelectorAll(
    "button[data-userid='id" + user_id_to_follow + "']"
  );
  follow_buttons.forEach((button) => {
    button.dataset.follows =
      button.dataset.follows == "True" ? "False" : "True";
    button.textContent =
      button.dataset.follows == "True" ? "FOLLOWING" : "FOLLOW";
  });
  // spa(window.location.pathname, false, event);
  event.target.classList.remove("disabled");
};

const open_home = (event) => {
  spa("/home", true, event);
};

const admin_delete_tweet = async (event) => {
  event.preventDefault();
  event.stopPropagation();
  // add elipses to indicate that something is happening
  const submit_button_value = event.target.textContent;
  event.target.textContent = "deleting...";
  event.target.classList.add("disabled");
  const tweet_id = event.target.id.slice(2);
  await fetch("/admin/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      spa(response.url, false, event);
      return;
    }
    // delete tweet from ui (could be done with spa, but this saves a get request)
    const tweet = document.querySelector(
      ".tweet_container[data-id='id" + tweet_id + "']"
    );
    tweet.remove();
    // spa("/admin", false, event);
  });
  // remove elipses
  event.target.textContent = submit_button_value;
  event.target.classList.remove("disabled");
};

const remove_selected_image = (event) => {
  event.preventDefault();
  event.stopPropagation();
  const image_input = document.querySelector("#tweet_image");
  image_input.value = "";
  const image_name_display = document.querySelector("#image_name");
  if (image_input.value == "") {
    image_name_display.value = "No image";
    image_name_display.textContent = "No image";
    document
      .querySelector("label[for='tweet_image']")
      .classList.remove("hidden");
    document.querySelector("#remove_image").classList.add("hidden");
  }
};

const tweet_image_changed = (event) => {
  const image_filename = document
    .querySelector("#tweet_image")
    .value.slice(
      document.querySelector("#tweet_image").value.lastIndexOf("\\") + 1
    );
  const image_name_display = document.querySelector("#image_name");
  if (image_filename !== "" && image_filename !== undefined) {
    image_name_display.value = image_filename;
    image_name_display.textContent = image_filename;
    document.querySelector("label[for='tweet_image']").classList.add("hidden");
    document.querySelector("#remove_image").classList.remove("hidden");
  } else {
    image_name_display.value = "No image";
  }
};
