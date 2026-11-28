
# ORION-Rover — PID et odométrie

## 1. Objectif

Le robot doit suivre une ligne au sol, contrôler la vitesse de ses moteurs et estimer ses déplacements.

## 2. Régulateur PID

Le PID utilise trois actions :

- Kp : correction proportionnelle à l'erreur.
- Ki : correction basée sur l'accumulation des erreurs.
- Kd : correction basée sur la variation de l'erreur.

### Formule PID discrète

u(k) = Kp × e(k) + Ki × somme(e(j) × Δt) + Kd × (e(k) - e(k-1)) / Δt

Avec :

- e(k) : erreur actuelle.
- Δt : période d'échantillonnage.
- Kp : gain proportionnel.
- Ki : gain intégral.
- Kd : gain dérivé.
- u(k) : commande de correction des moteurs.

## 3. Suivi de ligne

La barrette infrarouge 5 voies détecte la position de la ligne.

Le système doit :

1. Lire les cinq capteurs.
2. Déterminer la position de la ligne.
3. Calculer l'erreur.
4. Appliquer le PID.
5. Corriger la vitesse des deux moteurs.

## 4. Odométrie

Le robot utilise deux roues motrices.

Formules :

Δs = (dD + dG) / 2

Δθ = (dD - dG) / L

x(k+1) = x(k) + Δs × cos(θ)

y(k+1) = y(k) + Δs × sin(θ)

Avec :

- dD : distance parcourue par la roue droite.
- dG : distance parcourue par la roue gauche.
- L : distance entre les deux roues.
- θ : orientation du robot.
- x et y : position estimée.

## 5. Limitation matérielle

Les encodeurs des moteurs ne sont pas encore confirmés.

Sans encodeurs, le robot ne peut pas mesurer précisément la rotation des roues. L'odométrie réelle devra donc attendre leur installation.

## 6. Tests à effectuer

- Tester le suivi de ligne en ligne droite.
- Tester les virages.
- Ajuster Kp, Ki et Kd.
- Mesurer la stabilité du robot.
- Comparer les déplacements théoriques et réels lorsque les encodeurs seront disponibles.

## 7. Résultats attendus

- Code PID documenté.
- Paramètres Kp, Ki et Kd mesurés.
- Courbes d'essais.
- Documentation de l'odométrie.
