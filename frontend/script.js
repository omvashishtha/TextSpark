// =============================
// Show/Hide "Other" Inputs
// =============================

const categorySelect = document.getElementById("categorySelect");
const categoryOtherInput = document.getElementById("categoryOtherInput");

const targetSelect = document.getElementById("targetSelect");
const targetOtherInput = document.getElementById("targetOtherInput");

categorySelect.addEventListener("change", function () {
  categoryOtherInput.classList.toggle("hidden", this.value !== "Other");
});

targetSelect.addEventListener("change", function () {
  targetOtherInput.classList.toggle("hidden", this.value !== "Other");
});

// =============================
// Appwrite Setup
// =============================

const client = new Appwrite.Client();
client
  .setEndpoint("https://cloud.appwrite.io/v1") // Appwrite Endpoint
  .setProject("6886db01002d213e1f6a");         // Your Project ID

const databases = new Appwrite.Databases(client);

// =============================
// Form Submission Handler
// =============================

document.getElementById("campaignForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(e.target);

  let category = formData.get("category");
  if (category === "Other") {
    category = formData.get("category_other");
  }

  let target = formData.get("target");
  if (target === "Other") {
    target = formData.get("target_other");
  }

  const data = {
    business_name: formData.get("business_name"),
    description: formData.get("description"),
    category: category,
    target: target,
    status: "pending",
    timestamp: new Date().toISOString()
  };

  try {
    const response = await databases.createDocument(
      "6886dbd5003b445dffce",     // Database ID
      "6886dbe5000d34a52776",     // Collection ID (Campaigns)
      "unique()",                 // Document ID
      data
    );

    console.log("✅ Campaign created:", response);

    const result = document.getElementById("result");
    result.innerText = "✅ Campaign saved successfully!";
    result.classList.remove("hidden");
    result.classList.remove("text-red-400");
    result.classList.add("text-green-400");

    // Reset form
    e.target.reset();

    // Hide "Other" inputs after reset
    categoryOtherInput.classList.add("hidden");
    targetOtherInput.classList.add("hidden");

  } catch (error) {
    console.error("❌ Error saving campaign:", error);

    const result = document.getElementById("result");
    result.innerText = "❌ Something went wrong. Please try again.";
    result.classList.remove("hidden");
    result.classList.remove("text-green-400");
    result.classList.add("text-red-400");
  }
});
