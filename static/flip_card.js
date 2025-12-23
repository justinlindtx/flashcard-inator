// Cycle through cards in the set
let index = 0;
const containers = document.querySelectorAll('.card-container');
function showCard(n){
	if(n < 0 || n >= containers.length) return;
	containers[index].classList.remove('active');
	containers[index].querySelector('.card').classList.remove('is-flipped');
	index = n;
	containers[index].classList.add('active');
}
const prev = document.getElementById('btn-prev');
const next = document.getElementById('btn-next');
prev.addEventListener('click', () => {showCard(index - 1)});
next.addEventListener('click', () => {showCard(index + 1)});

// Flip on click
containers.forEach(container => {
	const card = container.querySelector('.card');
	container.addEventListener('click', () =>{
		card.classList.toggle('is-flipped');
	});
});
// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
	if(e.code === 'Space'){
		e.preventDefault(); // prevent scrolling
		containers[index].querySelector('.card').classList.toggle('is-flipped');
	}
	else if(e.code == 'ArrowRight'){
		showCard(index + 1);
	}
	else if(e.code == 'ArrowLeft'){
		showCard(index - 1);
	}
});
