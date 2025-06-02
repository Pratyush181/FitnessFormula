document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("fitness-form").addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent form submission
        try {
            const userData = {
                age: document.getElementById("age")?.value.trim(),
                height: document.getElementById("height")?.value.trim(),
                weight: document.getElementById("weight")?.value.trim(),
                gender: document.getElementById("gender")?.value.trim(),
                muscle_level: document.getElementById("muscle_level")?.value.trim(),
                fat_level: document.getElementById("fat_level")?.value.trim(),
                goal: document.getElementById("goal")?.value.trim(),
                workout_type: document.getElementById("workout_type")?.value.trim(),
            };

            console.log("User Data:", userData);

            if (Object.values(userData).some(value => !value)) {
                alert("Please fill out all fields before submitting.");
                return;
            }

            const response = await fetch("http://127.0.0.1:5000/calculate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const result = await response.json();
            console.log("Server Response:", result);

            document.getElementById("plan-output").innerHTML = `
                <p style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">
                    <strong style="color: #fff;">Your Status:</strong>
                </p>
                <div style="font-size: 14px; color: #ccc; margin-bottom: 15px;">
                    ${result.user_status.map(point => `<p style="margin: 5px 0;">${point}</p>`).join('')}
                </div>

                <p style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">
                    <strong style="color: #fff;">Workout Plan:</strong>
                </p>
                <p style="font-size: 24px; font-weight: bold; color: #007bff; margin-bottom: 5px;">
                    <a href="${result.workout_plan.url}" target="_blank" style="text-decoration: none; color: #007bff;">
                        ${result.workout_plan.name}
                    </a>
                </p>
                <p style="font-size: 14px; color: #ccc; margin-bottom: 15px;">
                    ${result.workout_plan.frequency} - ${result.workout_plan.summary}
                </p>
            
                <p style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">
                    <strong style="color: #fff;">Daily Steps Goal:</strong>
                </p>
                <p style="font-size: 28px; color: #e0e0e0; font-weight: bold; margin-bottom: 15px;">
                    ${result.daily_steps} steps
                </p>
                <br>

                <p style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">
                    <strong style="color: #fff;">Calories Goal:</strong>
                </p>
                <p style="font-size: 28px; color: #e0e0e0; font-weight: bold; margin-bottom: 15px;">
                    ${result.calories} kcal
                </p>
                <br>

                <p style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">
                    <strong style="color: #fff;">Protein Goal:</strong>
                </p>
                <p style="font-size: 28px; color: #e0e0e0; font-weight: bold;">
                    ${result.protein}g
                </p>
                <br>

                <p style="font-size: 14px; color: #007bff; margin-bottom: 15px;">
                    <a href="/DietPlans.html" style="text-decoration: none; color: #007bff;">
                        Click here to find healthy high-protein recipes
                    </a>
                </p>
            `;

        } catch (error) {
            console.error("Error fetching fitness plan:", error);
            alert("Failed to fetch fitness plan. Please try again.");
        }
    });

    document.getElementById("reset-btn").addEventListener("click", function () {
        document.querySelectorAll(".userInput").forEach(input => {
            if (input.tagName === "SELECT") {
                input.selectedIndex = 0;
            } else {
                input.value = "";
            }
        });

        document.getElementById("plan-output").innerHTML = "";
    });

    // Slideshow Logic
    let slideIndex = 0;
    showSlides();

    function showSlides() {
        let slides = document.getElementsByClassName("slide");
        
        // Remove active class from all slides
        for (let i = 0; i < slides.length; i++) {
            slides[i].classList.remove("active");
        }
        
        slideIndex++;
        if (slideIndex > slides.length) {
            slideIndex = 1;
        }
        
        // Add active class to current slide
        slides[slideIndex - 1].classList.add("active");
        
        // Schedule next slide
        setTimeout(showSlides, 5000); // Change slide every 5 seconds
    }
});

document.getElementById('fitnessForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = {
        age: 25, // Hardcoded for now; add input field later
        height: 175, // Hardcoded for now
        weight: parseInt(this.weight.value),
        gender: "male", // Hardcoded for now
        muscle_level: this.level.value.split(' ')[0].toLowerCase(), // e.g., "Beginner" -> "beginner"
        fat_level: "medium", // Hardcoded for now
        goal: "maintenance", // Hardcoded for now
        workout_type: "gym" // Hardcoded for now
    };
    const response = await fetch('http://localhost:5000/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    });
    const result = await response.json();
    document.getElementById('recommendation').innerText = `Plan: ${result.workout_plan.name} | Calories: ${result.calories} | Protein: ${result.protein}g`;
});