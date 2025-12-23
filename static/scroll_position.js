// Save scroll position before the page refreshes/closes
window.addEventListener('beforeunload', () => {
	localStorage.setItem('scrollPosition', window.scrollY);
});

// Restore scroll position when the page loads
window.addEventListener('load', () => {
	const scrollPos = localStorage.getItem('scrollPosition');
	if(scrollPos){
		window.scrollTo(0, parseInt(scrollPos));
		localStorage.removeItem('scrollPosition'); // Clean up
	}
});