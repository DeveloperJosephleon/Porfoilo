document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contact-form");
    const formStatus = document.getElementById("form-status");
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault(); // Prevent the default form submission
  
      // Gather form data
      const formData = {
        fullname: document.getElementById("fullname").value,
        email: document.getElementById("email").value,
        message: document.getElementById("message").value,
      };
  
      try {
        // Send the data to the backend using Fetch API
        const response = await fetch("/contact", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });
  
        const result = await response.json();
        if (response.ok) {
          formStatus.textContent = result.message; // Success message
          formStatus.style.color = "green";
          form.reset(); // Clear the form after successful submission
        } else {
          formStatus.textContent = result.error; // Error message
          formStatus.style.color = "red";
        }
      } catch (error) {
        formStatus.textContent = "An error occurred. Please try again.";
        formStatus.style.color = "red";
      }
    });
  });
  