////////////////////////////////////////////////////////////////////////////////////////////////////////
//      EXAMPLE OF INPUT WHERE THIS VALIDATION SYSTEM IS USED
////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// <label for="input" data-to-be-validated="true">
//
//     Label text
//
//     <span class="error_span hidden">Label text <span></span></span>
//
//     <input type="text" name="input" id="input" data-min="1" data-max="100" data-required="true" data-no-spaces="true">
//
// </label>
//
////////////////////////////////////////////////////////////////////////////////////////////////////////

//      will return 'true' if form is valid and 'false' if invalid
const validate = (form) => {
  //    validate labels
  const labels_to_validate = form.querySelectorAll("[data-to-be-validated]");
  if (labels_to_validate) {
    labels_to_validate.forEach((label) => {
      if (!label.dataset.toBeValidated) {
        return;
      }

      //      find input (might be a textarea)
      let input = label.querySelector("input");
      if (input == null) {
        input = label.querySelector("textarea");
        if (input == null) {
          return;
        }
      }

      //      remove previous errors
      input.classList.remove("validate_error");
      const error_message = label.querySelector("span.error_span");
      if (error_message) {
        error_message.classList.add("hidden");
      } else {
        return true;
      }

      //      called when a validation error is found
      const show_error = (error_text) => {
        input.classList.add("validate_error");
        error_message.classList.remove("hidden");
        error_message.querySelector("span").textContent = error_text;
      };

      //      required -- data-required="true"
      if (input.dataset.required && !input.value) {
        show_error("is required");
      }
      //      minimum length -- data-min="2"
      else if (input.dataset.min && input.dataset.min > input.value.length) {
        show_error("must be minimum " + input.dataset.min + " characters");
      }
      //      maximum length -- data-max="10"
      else if (input.dataset.max && input.dataset.max < input.value.length) {
        show_error("must be maximum " + input.dataset.max + " characters");
      }
      //      no spaces -- data-no-spaces="true"
      else if (input.dataset.noSpaces && input.value.includes(" ")) {
        show_error("can't contain spaces");
      }
      //      no special characters -- data-no-special-characters="true"
      else if (
        input.dataset.noSpecialCharacters &&
        !/^[A-Za-z0-9 ]+$/.test(input.value)
      ) {
        show_error("can't contain special characters");
      }
      //      email -- data-email="true"
      else if (
        input.dataset.email &&
        !/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
          input.value.toLowerCase()
        )
      ) {
        show_error("is not valid");
      }
      //      positive number -- data-positive-number="true"
      else if (input.dataset.positiveNumber && !/^\d+$/.test(input.value)) {
        show_error("must be a positive number");
      }
      //      number minimum value -- data-min-number="0"
      else if (
        input.dataset.minNumber &&
        parseInt(input.value) < parseInt(input.dataset.minNumber)
      ) {
        show_error("must be more than " + input.dataset.minNumber);
      }
      //      number maximum value -- data-max-number="10"
      else if (
        input.dataset.maxNumber &&
        parseInt(input.value) > parseInt(input.dataset.maxNumber)
      ) {
        show_error("must be less than " + input.dataset.maxNumber);
      }
    });
  }

  //      check if form is valid
  if (!form.querySelector(".validate_error")) {
    //      valid! return true!
    return true;
  } else {
    //      not valid return false
    //      focus on first error and move cursor to end of input value
    const input = form.querySelector(".validate_error");
    input.selectionStart = input.selectionEnd = input.value.length;
    input.focus();
    return false;
  }
};
