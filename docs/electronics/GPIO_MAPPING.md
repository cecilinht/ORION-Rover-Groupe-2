
# ORION-Rover — Plan GPIO ESP32

## 1. Carte utilisée

- Microcontrôleur : ESP32 DevKit V1
- Module : ESP32-WROOM-32
- Tension logique : 3,3 V
- Communication : Wi-Fi

## 2. Composants connectés

- Driver moteur L298N
- 2 moteurs DC
- 3 capteurs ultrasoniques HC-SR04
- 1 barrette infrarouge 5 voies
- 1 capteur MPU6050

## 3. Broches réservées

| Fonction | GPIO |
|---|---|
| MPU6050 SDA | 21 |
| MPU6050 SCL | 22 |

## 4. Proposition de brochage moteur

| L298N | ESP32 |
|---|---|
| ENA | GPIO25 |
| IN1 | GPIO26 |
| IN2 | GPIO27 |
| ENB | GPIO14 |
| IN3 | GPIO13 |
| IN4 | GPIO23 |

## 5. Capteurs ultrasoniques

| Capteur | TRIG | ECHO |
|---|---|---|
| Avant | GPIO18 | GPIO34 |
| Gauche | GPIO19 | GPIO35 |
| Droite | À définir | GPIO36 |

## 6. Sécurité électrique

- Les broches ESP32 fonctionnent en logique 3,3 V.
- Ne jamais connecter directement un ECHO HC-SR04 de 5 V à une entrée ESP32.
- Utiliser un pont diviseur de tension sur chaque sortie ECHO.
- Relier les masses GND des modules.
- Alimenter les moteurs séparément de la logique ESP32.

## 7. Broches restant à définir

- TRIG du capteur ultrasonique droit.
- Les cinq sorties de la barrette infrarouge.
- Les éventuelles broches supplémentaires nécessaires.

## 8. Validation

Ce plan est provisoire. Le câblage définitif doit être validé avec le modèle exact des modules, les broches disponibles et les tests électriques.
