# Démonstrations et Formules Mathématiques — Projet ORION-Rover (Groupe 2)

**Atelier pilote TECH V2 – ORION UNIVERSITY (Novembre 2026)**
**Thème A :** Robot livreur autonome du campus

---

## 1. Mesure de distance par ultrason (Capteurs HC-SR04)

### Formule
$$d = \frac{v \times t}{2}$$

### Signification des variables
* **$d$** : distance entre le capteur ultrason et l'obstacle (en mètres $\text{m}$, ou en centimètres $\text{cm}$).
* **$v$** : vitesse de propagation du son dans l'air ($v \approx 343\text{ m/s}$, soit $0{,}0343\text{ cm/}\mu\text{s}$ à $20^\circ\text{C}$).
* **$t$** : durée totale d'aller-retour de l'onde ultrasonore entre l'émission (`TRIG`) et la réception de l'écho (`ECHO`) (en secondes $\text{s}$, ou en microsecondes $\mu\text{s}$).
* **$\div 2$** : division par $2$ car l'onde sonore parcourt deux fois la distance $d$ (trajet aller + trajet retour).

### Rôle dans le robot
Mesurer en continu la distance devant, à gauche et à droite du rover pour activer les **3 zones de sécurité** (Verte $> 40\text{ cm}$, Orange $15\text{–}40\text{ cm}$, Rouge $< 15\text{ cm}$).

---

## 2. Filtrage numérique par moyenne glissante

### Formule
$$\bar{d}(k) = \frac{1}{N} \sum_{i=0}^{N-1} d(k - i) = \frac{d(k) + d(k-1) + d(k-2)}{3} \quad (\text{pour } N = 3)$$

### Signification des variables
* **$\bar{d}(k)$** : distance filtrée (lissée) à l'instant actuel $k$ (en $\text{cm}$).
* **$N$** : taille de la fenêtre glissante, soit le nombre de mesures consécutives utilisées ($N = 3$ dans notre firmware ESP32).
* **$d(k)$** : mesure brute actuelle du capteur ultrason à l'instant $k$ (en $\text{cm}$).
* **$d(k-1), d(k-2)$** : les deux mesures brutes précédentes (en $\text{cm}$).

### Rôle dans le robot
Éliminer les parasites acoustiques et les pics erronés ponctuels des capteurs HC-SR04 afin d'éviter un freinage d'urgence injustifié.

---

## 3. Cinématique différentielle et Odométrie (Localisation 2D)

### Formules
1. **Distance parcourue par chaque roue :**
   $$d_G = \Delta N_G \times \frac{2\pi R}{N_{\text{tours}}} \qquad ; \qquad d_D = \Delta N_D \times \frac{2\pi R}{N_{\text{tours}}}$$
2. **Déplacement linéaire moyen et variation d'orientation :**
   $$\Delta s = \frac{d_D + d_G}{2} \qquad ; \qquad \Delta\theta = \frac{d_D - d_G}{L}$$
3. **Mise à jour de la position $(x, y)$ et du cap $\theta$ (Matrice de rotation 2D) :**
   $$x(k+1) = x(k) + \Delta s \cdot \cos\theta(k)$$
   $$y(k+1) = y(k) + \Delta s \cdot \sin\theta(k)$$
   $$\theta(k+1) = \theta(k) + \Delta\theta$$

### Signification des variables
* **$d_G, d_D$** : distances parcourues respectivement par la roue gauche et la roue droite pendant $\Delta t$ (en $\text{cm}$).
* **$\Delta N_G, \Delta N_D$** : nombre d'impulsions (*ticks*) comptées par les encodeurs gauche et droit.
* **$R$** : rayon d'une roue motrice ($R = 3{,}25\text{ cm}$).
* **$N_{\text{tours}}$** : nombre d'impulsions de l'encodeur pour un tour complet de roue ($N_{\text{tours}} = 20$).
* **$L$** : entraxe du robot, soit la distance entre le centre de la roue gauche et le centre de la roue droite ($L = 15{,}0\text{ cm}$).
* **$\Delta s$** : déplacement linéaire moyen du centre du robot (en $\text{cm}$).
* **$\Delta\theta$** : variation de l'angle de rotation du robot (en radians $\text{rad}$).
* **$x(k), y(k)$** : coordonnées cartésiennes du robot sur le circuit à l'instant $k$ (en $\text{cm}$).
* **$\theta(k)$** : angle d'orientation (cap) du robot par rapport à l'axe $X$ à l'instant $k$ (en $\text{rad}$).

---

## 4. Régulateur PID discret (Asservissement du suivi de ligne)

### Formules
1. **Erreur de position sur la barrette 5 capteurs IR :**
   $$e(k) = \frac{\sum_{i=1}^{5} w_i \cdot c_i(k)}{\sum_{i=1}^{5} c_i(k)} \quad \text{avec } w = [-2, -1, 0, +1, +2]$$
2. **Loi de commande PID discrète :**
   $$u(k) = K_p \cdot e(k) + K_i \sum_{j=0}^{k} e(j)\,\Delta t + K_d \cdot \frac{e(k) - e(k-1)}{\Delta t}$$
3. **Commande des moteurs gauche et droit (PWM) :**
   $$\text{PWM}_G = V_{\text{base}} + u(k) \qquad ; \qquad \text{PWM}_D = V_{\text{base}} - u(k)$$

### Signification des variables
* **$e(k)$** : erreur de centrage par rapport à la ligne noire à l'instant $k$ ($e = 0$ si centré, $e < 0$ à gauche, $e > 0$ à droite).
* **$w_i$** : poids géométrique attribué au capteur IR $i$ ($-2$ extrême gauche, $0$ centre, $+2$ extrême droite).
* **$c_i(k)$** : état logique du capteur IR $i$ ($1$ si ligne noire détectée, $0$ sinon).
* **$u(k)$** : signal de correction calculé par le PID à l'instant $k$.
* **$\Delta t$** : période d'échantillonnage de la boucle de contrôle ($\Delta t = 0{,}05\text{ s}$, soit $20\text{ Hz}$).
* **$K_p$** : gain **Proportionnel** (réagit immédiatement à l'écart actuel).
* **$K_i$** : gain **Intégral** (corrige l'accumulation des petites erreurs persistantes).
* **$K_d$** : gain **Dérivé** (anticipe la vitesse de variation de l'erreur pour limiter les oscillations).
* **$V_{\text{base}}$** : vitesse de base des moteurs en PWM ($0$ à $255$).
* **$\text{PWM}_G, \text{PWM}_D$** : signaux PWM envoyés au driver L298N pour les roues gauche et droite.

---

## 5. Loi proportionnelle de ralentissement (Zone Orange)

### Formule
$$V_{\text{réduite}} = V_{\min} + \left(\frac{d_{\text{avant}} - d_{\min}}{d_{\max} - d_{\min}}\right) \times (V_{\text{base}} - V_{\min})$$

### Signification des variables
* **$V_{\text{réduite}}$** : vitesse ajustée dans la zone orange (en PWM).
* **$V_{\min}$** : vitesse minimale sans calage des moteurs ($V_{\min} = 90\text{ PWM}$).
* **$V_{\text{base}}$** : vitesse normale en zone verte ($V_{\text{base}} = 165\text{ PWM}$).
* **$d_{\text{avant}}$** : distance mesurée par le capteur ultrason avant (en $\text{cm}$).
* **$d_{\min}, d_{\max}$** : bornes de la zone orange ($d_{\min} = 15\text{ cm}$, $d_{\max} = 40\text{ cm}$).

---

## 6. Pont diviseur de tension (Protection électronique & Batterie)

### Formule
$$V_{\text{out}} = V_{\text{in}} \times \frac{R_2}{R_1 + R_2}$$

### Signification des variables
* **$V_{\text{in}}$** : tension d'entrée haute à mesurer ou abaisser (en Volts $\text{V}$).
* **$V_{\text{out}}$** : tension de sortie abaissée envoyée vers l'ESP32 ($\le 3{,}3\text{ V}$).
* **$R_1$** : résistance reliée entre $V_{\text{in}}$ et le point de mesure GPIO (en Ohms $\Omega$).
* **$R_2$** : résistance reliée entre le point de mesure GPIO et la masse `GND` (en Ohms $\Omega$).

### Valeurs calculées pour le robot
1. **Signal `ECHO` ultrasons HC-SR04 ($5\text{ V} \rightarrow 3{,}33\text{ V}$) :** $R_1 = 1\text{ k}\Omega$, $R_2 = 2\text{ k}\Omega$.
2. **Batterie Li-ion 2S ($8{,}4\text{ V max} \rightarrow 2{,}80\text{ V}$) :** $R_1 = 20\text{ k}\Omega$ (ou $2 \times 10\text{ k}\Omega$ en série), $R_2 = 10\text{ k}\Omega$.

---

## 7. Intelligence Artificielle et Statistiques d'évaluation

### Formules
1. **Fonction Softmax (score de confiance CNN) :**
   $$P(y = c \mid x) = \frac{e^{z_c}}{\sum_{j=1}^{K} e^{z_j}}$$
2. **Métriques de la matrice de confusion :**
   $$\text{Précision}_c = \frac{VP_c}{VP_c + FP_c} \quad ; \quad \text{Rappel}_c = \frac{VP_c}{VP_c + FN_c} \quad ; \quad \text{Accuracy} = \frac{\sum_{c=1}^{K} VP_c}{N_{\text{total}}}$$
3. **Moyenne, Écart-type et Erreur de position finale :**
   $$\mu = \frac{1}{n}\sum_{i=1}^{n} x_i \quad ; \quad \sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2} \quad ; \quad E_{\text{pos}} = \sqrt{(x_{\text{odom}} - x_{\text{réel}})^2 + (y_{\text{odom}} - y_{\text{réel}})^2}$$

### Signification des variables
* **$z_c$** : score brut (*logit*) produit par le réseau CNN pour la classe $c$.
* **$K$** : nombre total de classes de panneaux ($K = 6$).
* **$P(y = c \mid x)$** : probabilité estimée (score de confiance) que l'image $x$ appartienne à la classe $c$.
* **$VP_c, FP_c, FN_c$** : Vrais Positifs, Faux Positifs et Faux Négatifs pour la classe $c$.
* **$N_{\text{total}}$** : nombre total d'images du jeu de test ($438$ images, $\text{Accuracy} = 98{,}86\,\%$).
* **$\mu$** : moyenne arithmétique d'une série de $n$ mesures $x_i$ (ex. temps de parcours moyen).
* **$\sigma$** : écart-type mesurant la régularité des mesures autour de $\mu$.
* **$E_{\text{pos}}$** : erreur euclidienne entre la position calculée par odométrie $(x_{\text{odom}}, y_{\text{odom}})$ et la position réelle mesurée sur le circuit $(x_{\text{réel}}, y_{\text{réel}})$ (en $\text{cm}$).
