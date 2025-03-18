document.addEventListener('DOMContentLoaded', function() {
  // Initialize date pickers
  flatpickr('.date-picker', {
    dateFormat: 'm/d/Y',
    allowInput: true
  });
  
  // Theme toggle functionality
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;
  const toggleIcon = document.querySelector('.toggle-icon');
  const toggleText = document.querySelector('.toggle-text');
  
  // Check for saved theme preference
  const savedTheme = localStorage.getItem('mileage-theme');
  if (savedTheme === 'dark') {
    body.classList.remove('light-mode');
    body.classList.add('dark-mode');
    toggleIcon.textContent = '☀️';
    toggleText.textContent = 'Light Mode';
  }
  
  // Toggle theme on button click
  themeToggle.addEventListener('click', function() {
    if (body.classList.contains('light-mode')) {
      body.classList.remove('light-mode');
      body.classList.add('dark-mode');
      toggleIcon.textContent = '☀️';
      toggleText.textContent = 'Light Mode';
      localStorage.setItem('mileage-theme', 'dark');
    } else {
      body.classList.remove('dark-mode');
      body.classList.add('light-mode');
      toggleIcon.textContent = '🌙';
      toggleText.textContent = 'Dark Mode';
      localStorage.setItem('mileage-theme', 'light');
    }
  });
  
  // Calculate total miles
  const form = document.getElementById('mileage-form');
  const totalBusinessMilesInput = document.getElementById('total-business-miles');
  const totalMilesInput = document.getElementById('total-miles');
  const totalAmountInput = document.getElementById('total-amount');
  
  // Function to calculate totals
  function calculateTotals() {
    const totalMilesInputs = document.querySelectorAll('.total-miles');
    let totalMiles = 0;
    
    totalMilesInputs.forEach(input => {
      const miles = parseFloat(input.value) || 0;
      totalMiles += miles;
    });
    
    totalBusinessMilesInput.value = totalMiles.toFixed(2);
    totalMilesInput.value = totalMiles.toFixed(2);
    
    // Calculate reimbursement amount (rate is $0.70 per mile)
    const rate = 0.70;
    const reimbursementAmount = totalMiles * rate;
    totalAmountInput.value = reimbursementAmount.toFixed(2);
  }
  
  // Add event listeners to all total miles inputs
  const totalMilesInputs = document.querySelectorAll('.total-miles');
  totalMilesInputs.forEach(input => {
    input.addEventListener('input', calculateTotals);
  });
  
  // Form submission
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Recalculate totals before submission
    calculateTotals();
    
    // Collect form data
    const formData = new FormData(form);
    
    // Debug: Log form data
    console.log("Submitting form data:");
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }
    
    // Send form data to server
    fetch('/api/mileage', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.error || 'Network response was not ok');
        });
      }
      return response.json();
    })
    .then(data => {
      console.log("Success response:", data);
      alert(data.message || 'Mileage report submitted successfully!');
      form.reset();
    })
    .catch(error => {
      console.error('Error:', error);
      alert('There was a problem submitting your mileage report. Please try again.');
    });
  });
  
  // Initialize calculations on page load
  calculateTotals();
});
