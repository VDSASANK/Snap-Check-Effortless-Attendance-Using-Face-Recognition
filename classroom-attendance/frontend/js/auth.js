import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

const auth = getAuth();
const db = getFirestore();

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorDisplay = document.getElementById("loginError");

  // Clear any previous error messages
  errorDisplay.textContent = '';
  errorDisplay.classList.add("hidden");

  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    const uid = user.uid;

    const userRef = doc(db, "users", uid);
    const userSnap = await getDoc(userRef);

    if (userSnap.exists()) {
      const userData = userSnap.data();

      // Redirect based on role
      if (userData.role === "student") {
        window.location.href = "student_dashboard.html";
      } else if (userData.role === "teacher") {
        window.location.href = "teacher_dashboard.html";
      } else {
        errorDisplay.textContent = "User role not defined.";
        errorDisplay.classList.remove("hidden");
      }
    } else {
      errorDisplay.textContent = "No user data found.";
      errorDisplay.classList.remove("hidden");
    }
  } catch (error) {
    errorDisplay.textContent = "Error: " + error.message;
    errorDisplay.classList.remove("hidden");
  }
});
