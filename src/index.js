import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import gsap from 'gsap';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcad8c3); // 🔳 grigio molto scuro

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.update();

// 💡 Luce ambientale (luce diffusa ovunque)
scene.add(new THREE.AmbientLight(0xffffff, 1.2)); // da 0.8 → 1.2


// 💡 Luce direzionale principale
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
directionalLight.position.set(5, 10, 7);
directionalLight.castShadow = true;
scene.add(directionalLight);

// 💡 Luce emisferica (cielo/terra)
const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
hemisphereLight.position.set(0, 20, 0);
scene.add(hemisphereLight);
let model;
const scompartiAttivi = new Map(); // es: { "Cassetto1": Scomparto4 }
const cassettiAperti = new Set();


const loader = new GLTFLoader();
loader.load('carrello3.glb', (gltf) => {
    model = gltf.scene;
    // 🔁 Sovrascrive i materiali scuri
    model.traverse((node) => {
        if (node.isMesh && node.name === "Carrello") {
            node.material.color.set(0xffffff); // forza bianco puro
        }
    });
    model.position.y += 1; // ⬆️ Alza leggermente il modello
    model.rotation.y = -Math.PI / 2 - Math.PI / 5; // Rotazione di 45 gradi su X (in radianti)
    const carrello = model.getObjectByName("Cassetto1");
    const scomparto = model.getObjectByName("Scomparto3");
    if (scomparto) {
        scomparto.traverse(node => {
            if (node.isMesh && node.material) {
                node.material.color.set(0xFFFFFF);
                node.material.metalness = 0.0;         // no metallo
                node.material.roughness = 0;
                node.material.needsUpdate = true;
            }
        });
    }


    const cassetto2 = model.getObjectByName("Cassetto2");
    if (cassetto2) {
        const initialX = cassetto2.position.x; // salva la posizione iniziale
        //set positionx to initialX -0.1
        cassetto2.position.x = initialX - 0.01;
    }

    const cassetto3 = model.getObjectByName("Cassetto3");
    if (cassetto3) {
        const initialX = cassetto3.position.x; // salva la posizione iniziale
        //set positionx to initialX -0.1
        cassetto3.position.x = initialX - 0.01;
    }




    scene.add(model);
    model.traverse(obj => console.log(obj.name));
}, undefined, err => console.error('Errore GLB', err));


// Funzione per aprire un cassetto
function apriCassetto(nomeCassetto) {
    if (cassettiAperti.has(nomeCassetto)) return; // già aperto, ignora

    const cassetto = model.getObjectByName(nomeCassetto);
    if (!cassetto) return;

    cassettiAperti.add(nomeCassetto);
    const initialX = cassetto.position.x;

    gsap.to(cassetto.position, {
        x: initialX + 1,
        duration: 1.0,
        ease: "power2.out"
    });
}
function chiudiCassetto(nomeCassetto) {
    if (!cassettiAperti.has(nomeCassetto)) return; // già chiuso

    const cassetto = model.getObjectByName(nomeCassetto);
    if (!cassetto) return;

    const initialX = cassetto.userData.initialX ?? (cassetto.userData.initialX = cassetto.position.x - 1);

    gsap.to(cassetto.position, {
        x: initialX,
        duration: 1.0,
        ease: "power2.inOut",
        onComplete: () => {
            spegniScompartoAssociato(nomeCassetto);
            cassettiAperti.delete(nomeCassetto);
        }
    });
}
window.chiudiCassetto = chiudiCassetto;
window.spegniScompartoAssociato = spegniScompartoAssociato;

function illuminaScompartoDaIntervallo(cassetto, min, max) {
    const index = Math.floor(Math.random() * (max - min + 1)) + min;
    const scomparto = model.getObjectByName(`Scomparto${index}`);

    if (scomparto) {
        scomparto.traverse(node => {
            if (node.isMesh && node.material) {
                node.material = node.material.clone();
                node.material.color.set(0x00ff00); // verde brillante
                node.material.needsUpdate = true;
            }
        });
        scompartiAttivi.set(cassetto, scomparto); // memorizza il riferimento
    }
}
function spegniScompartoAssociato(cassetto) {
    const scomparto = scompartiAttivi.get(cassetto);
    if (scomparto) {
        scomparto.traverse(node => {
            if (node.isMesh && node.material) {
                node.material.color.set(0xffffff); // torna bianco (o altro colore originale)
                node.material.needsUpdate = true;
            }
        });
        scompartiAttivi.delete(cassetto);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('controls').addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            const nomeCassetto = event.target.getAttribute('data-cassetto');
            apriCassetto(nomeCassetto);

            // Determina intervallo scomparti
            if (nomeCassetto === "Cassetto1") {
                illuminaScompartoDaIntervallo("Cassetto1", 1, 6);
            } else if (nomeCassetto === "Cassetto2") {
                illuminaScompartoDaIntervallo("Cassetto2", 7, 12);
            } else if (nomeCassetto === "Cassetto3") {
                illuminaScompartoDaIntervallo("Cassetto3", 13, 18);
            }
        }
    });
});
window.apriCassetto = function (nomeCassetto) {
    apriCassetto(nomeCassetto);

    if (nomeCassetto === "Cassetto1") {
        illuminaScompartoDaIntervallo("Cassetto1", 1, 6);
    } else if (nomeCassetto === "Cassetto2") {
        illuminaScompartoDaIntervallo("Cassetto2", 7, 12);
    } else if (nomeCassetto === "Cassetto3") {
        illuminaScompartoDaIntervallo("Cassetto3", 13, 18);
    }
};
window.apriScomparto = function (cassetto, scomparto) {
    apriCassetto(`Cassetto${cassetto}`);
    illuminaScompartoDaIntervallo(`Cassetto${cassetto}`, scomparto, scomparto);
};
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
