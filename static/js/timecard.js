document.addEventListener('DOMContentLoaded', function() {
  // Initialize theme based on local storage or default to light
  const savedTheme = localStorage.getItem('theme') || 'light';
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    document.getElementById('theme-toggle').querySelector('.toggle-icon').textContent = '☀️';
    document.getElementById('theme-toggle').querySelector('.toggle-text').textContent = 'Light Mode';
  }

  // Theme toggle functionality
  document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const toggleIcon = this.querySelector('.toggle-icon');
    const toggleText = this.querySelector('.toggle-text');
    
    if (body.classList.contains('dark-mode')) {
      body.classList.remove('dark-mode');
      toggleIcon.textContent = '🌙';
      toggleText.textContent = 'Dark Mode';
      localStorage.setItem('theme', 'light');
    } else {
      body.classList.add('dark-mode');
      toggleIcon.textContent = '☀️';
      toggleText.textContent = 'Light Mode';
      localStorage.setItem('theme', 'dark');
    }
  });

  // Initialize date pickers
  const datePickers = document.querySelectorAll('.date-picker');
  datePickers.forEach(picker => {
    flatpickr(picker, {
      dateFormat: "m/d/Y",
      defaultDate: new Date()
    });
  });

  // Initialize time pickers with 5 AM start
  const timePickers = document.querySelectorAll('.time-picker');
  timePickers.forEach(picker => {
    flatpickr(picker, {
      enableTime: true,
      noCalendar: true,
      dateFormat: "h:i K", // 12-hour format with AM/PM
      time_24hr: false,
      minuteIncrement: 15,
      defaultHour: 5, // Start at 5 AM
      defaultMinute: 0
    });
  });

  // Calculate daily totals when time inputs change
  const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  
  days.forEach(day => {
    const timeIn = document.querySelector(`[name="${day}-time-in"]`);
    const lunchOut = document.querySelector(`[name="${day}-lunch-out"]`);
    const lunchIn = document.querySelector(`[name="${day}-lunch-in"]`);
    const timeOut = document.querySelector(`[name="${day}-time-out"]`);
    const totalField = document.querySelector(`[name="${day}-total"]`);
    
    [timeIn, lunchOut, lunchIn, timeOut].forEach(input => {
      if (input) {
        input.addEventListener('change', () => calculateDailyTotal(day));
      }
    });
  });

  // Function to calculate daily total hours
  function calculateDailyTotal(day) {
    const timeIn = document.querySelector(`[name="${day}-time-in"]`).value;
    const lunchOut = document.querySelector(`[name="${day}-lunch-out"]`).value;
    const lunchIn = document.querySelector(`[name="${day}-lunch-in"]`).value;
    const timeOut = document.querySelector(`[name="${day}-time-out"]`).value;
    const totalField = document.querySelector(`[name="${day}-total"]`);
    
    if (!timeIn || !timeOut) {
      totalField.value = '';
      return;
    }
    
    // Convert time strings to Date objects for calculation
    const timeInDate = parseTimeString(timeIn);
    const timeOutDate = parseTimeString(timeOut);
    
    let totalHours = (timeOutDate - timeInDate) / (1000 * 60 * 60); // Hours
    
    // Subtract lunch break if both lunch times are provided
    if (lunchOut && lunchIn) {
      const lunchOutDate = parseTimeString(lunchOut);
      const lunchInDate = parseTimeString(lunchIn);
      const lunchHours = (lunchInDate - lunchOutDate) / (1000 * 60 * 60);
      totalHours -= lunchHours;
    }
    
    // Format the total hours
    totalField.value = totalHours.toFixed(2);
  }

  // Helper function to parse time strings like "5:00 AM" into Date objects
  function parseTimeString(timeStr) {
    if (!timeStr) return null;
    
    const [time, period] = timeStr.split(' ');
    let [hours, minutes] = time.split(':').map(Number);
    
    // Convert to 24-hour format for calculation
    if (period === 'PM' && hours < 12) {
      hours += 12;
    } else if (period === 'AM' && hours === 12) {
      hours = 0;
    }
    
    const date = new Date();
    date.setHours(hours, minutes, 0, 0);
    return date;
  }

  // Form submission handler
  document.getElementById('timecard-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = new FormData(this);
    
    // Send form data to server
    fetch('/api/timecard', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      alert('Form submitted successfully! Email has been sent to timecardcorrection@MERITALUMINUM.COM');
      // Optionally reset the form
      document.getElementById('timecard-form').reset();
    })
    .catch(error => {
      console.error('Error:', error);
      alert('There was an error submitting the form. Please try again.');
    });
  });
});
