document.addEventListener('DOMContentLoaded', () => {
  const dugme = document.querySelector('.meni-dugme');
  const meni = document.getElementById('glavni-meni');
  dugme.addEventListener('click', () => {
    const otvoren = meni.classList.toggle('otvoren');
    dugme.setAttribute('aria-expanded', String(otvoren));
  });
  // baner se upisuje u unaprijed rezervisan prostor, pa ne pomjera sadržaj
  setTimeout(() => {
    document.getElementById('baner').textContent =
      'Ljetni popust 20% na sve ture! Rezervišite do kraja mjeseca.';
  }, 1200);
});
