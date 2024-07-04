import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
LARGEUR = 800
HAUTEUR = 600

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)

# Création de l'écran
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Galaxia Avancé")

# Classe pour le vaisseau du joueur
class Vaisseau(pygame.sprite.Sprite):
    def __init__(self, type_vaisseau):
        super().__init__()
        self.type_vaisseau = type_vaisseau
        self.image = self.creer_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGEUR // 2
        self.rect.bottom = HAUTEUR - 10
        self.vitesse = 5
        self.bouclier = 100
        self.xp = 0
        self.niveau_joueur = 1
        self.capacite_bouclier = 0
        self.capacite_explosion = 0
        self.type_laser = 'normal'
        self.combo = 0
        self.temps_dernier_kill = 0
        self.pimpage = {
            'vitesse': 0,
            'bouclier': 0,
            'puissance_tir': 0
        }

    def creer_image(self):
        image = pygame.Surface((40, 50), pygame.SRCALPHA)
        if self.type_vaisseau == 'standard':
            pygame.draw.polygon(image, BLANC, [(20, 0), (0, 50), (40, 50)])
            pygame.draw.rect(image, BLEU, (15, 35, 10, 15))
        elif self.type_vaisseau == 'rapide':
            pygame.draw.polygon(image, VERT, [(20, 0), (0, 50), (40, 50)])
            pygame.draw.rect(image, JAUNE, (15, 35, 10, 15))
        elif self.type_vaisseau == 'puissant':
            pygame.draw.polygon(image, ROUGE, [(20, 0), (0, 50), (40, 50)])
            pygame.draw.rect(image, BLANC, (15, 35, 10, 15))
        return image

    def update(self):
        touches = pygame.key.get_pressed()
        if (touches[pygame.K_LEFT] or touches[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.vitesse + self.pimpage['vitesse']
        if (touches[pygame.K_RIGHT] or touches[pygame.K_d]) and self.rect.right < LARGEUR:
            self.rect.x += self.vitesse + self.pimpage['vitesse']
        if (touches[pygame.K_UP] or touches[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.vitesse + self.pimpage['vitesse']
        if (touches[pygame.K_DOWN] or touches[pygame.K_s]) and self.rect.bottom < HAUTEUR:
            self.rect.y += self.vitesse + self.pimpage['vitesse']

        if self.capacite_bouclier > 0:
            self.capacite_bouclier -= 1
        if self.capacite_explosion > 0:
            self.capacite_explosion -= 1

    def tirer(self):
        if self.type_laser == 'normal':
            return Laser(self.rect.centerx, self.rect.top, self.pimpage['puissance_tir'])
        elif self.type_laser == 'rapide':
            return LaserRapide(self.rect.centerx, self.rect.top, self.pimpage['puissance_tir'])
        elif self.type_laser == 'puissant':
            return LaserPuissant(self.rect.centerx, self.rect.top, self.pimpage['puissance_tir'])

    def gagner_xp(self, quantite):
        self.xp += quantite
        if self.xp >= self.niveau_joueur * 100:
            self.monter_niveau()

    def monter_niveau(self):
        self.niveau_joueur += 1
        self.vitesse += 0.5
        self.bouclier += 20

    def utiliser_bouclier(self):
        if self.capacite_bouclier == 0:
            self.bouclier = 100 + self.pimpage['bouclier']
            self.capacite_bouclier = 600  # 10 secondes de recharge

    def utiliser_explosion(self):
        if self.capacite_explosion == 0:
            self.capacite_explosion = 1800  # 30 secondes de recharge
            return True
        return False

    def incrementer_combo(self):
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - self.temps_dernier_kill < 1000:  # 1 seconde
            self.combo += 1
        else:
            self.combo = 0
        self.temps_dernier_kill = temps_actuel

    def calculer_score(self, score_base):
        return score_base * (1 + self.combo * 0.1)

# Classe pour les lasers
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, puissance_supplementaire=0):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill(VERT)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vitesse = -10
        self.puissance = 10 + puissance_supplementaire

    def update(self):
        self.rect.y += self.vitesse
        if self.rect.bottom < 0:
            self.kill()

class LaserRapide(Laser):
    def __init__(self, x, y, puissance_supplementaire=0):
        super().__init__(x, y, puissance_supplementaire)
        self.image.fill(BLEU)
        self.vitesse = -15
        self.puissance = 5 + puissance_supplementaire

class LaserPuissant(Laser):
    def __init__(self, x, y, puissance_supplementaire=0):
        super().__init__(x, y, puissance_supplementaire)
        self.image = pygame.Surface((8, 30))
        self.image.fill(ROUGE)
        self.vitesse = -8
        self.puissance = 20 + puissance_supplementaire

# Classe pour les ennemis
class Ennemi(pygame.sprite.Sprite):
    def __init__(self, niveau):
        super().__init__()
        self.niveau = niveau
        self.image = self.creer_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.vitesse = random.randint(1, 3 + self.niveau)
        self.direction = random.choice([-1, 1])
        self.vie = 10 * self.niveau

    def creer_image(self):
        if self.niveau == 1:
            image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(image, ROUGE, (15, 15), 15)
        elif self.niveau == 2:
            image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(image, JAUNE, [(20, 0), (40, 40), (0, 40)])
        else:
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(image, BLEU, (0, 0, 50, 50))
            pygame.draw.circle(image, ROUGE, (25, 25), 15)
        return image

    def update(self):
        self.rect.y += self.vitesse
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > LARGEUR:
            self.direction *= -1
        if self.rect.top > HAUTEUR:
            self.rect.x = random.randint(0, LARGEUR - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.vitesse = random.randint(1, 3 + self.niveau)

# Classe pour le boss
class Boss(pygame.sprite.Sprite):
    def __init__(self, niveau):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.image, ROUGE, (0, 0, 100, 100))
        pygame.draw.circle(self.image, JAUNE, (50, 50), 30)
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGEUR // 2
        self.rect.top = -self.rect.height
        self.vie = 100 * niveau
        self.vitesse = 2
        self.phase = 'descente'
        self.temps_dernier_tir = 0

    def update(self):
        if self.phase == 'descente':
            self.rect.y += self.vitesse
            if self.rect.top >= 50:
                self.phase = 'combat'
        elif self.phase == 'combat':
            self.rect.x += math.sin(pygame.time.get_ticks() * 0.005) * 5

    def tirer(self):
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - self.temps_dernier_tir > 1000:  # Tir toutes les secondes
            self.temps_dernier_tir = temps_actuel
            return [Laser(self.rect.centerx, self.rect.bottom) for _ in range(3)]
        return []

# Classe pour les power-ups
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['bouclier', 'vitesse', 'tir_multiple'])
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        if self.type == 'bouclier':
            pygame.draw.circle(self.image, BLEU, (10, 10), 10)
        elif self.type == 'vitesse':
            pygame.draw.polygon(self.image, VERT, [(10, 0), (20, 20), (0, 20)])
        else:
            pygame.draw.rect(self.image, JAUNE, (0, 0, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = -self.rect.height
        self.vitesse = 2

    def update(self):
        self.rect.y += self.vitesse
        if self.rect.top > HAUTEUR:
            self.kill()

# Classe pour les astéroïdes
class Asteroide(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 100, 100), (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.vitesse = random.randint(1, 3)
        self.ressources = random.randint(10, 50)

    def update(self):
        self.rect.y += self.vitesse
        if self.rect.top > HAUTEUR:
            self.rect.x = random.randint(0, LARGEUR - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.vitesse = random.randint(1, 3)

# Classe pour les zones de danger
class ZoneDanger(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 128))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR - self.rect.width)
        self.rect.y = random.randint(0, HAUTEUR - self.rect.height)
        self.duree = 300  # 5 secondes

    def update(self):
        self.duree -= 1
        if self.duree <= 0:
            self.kill()

# Classe pour les étoiles (arrière-plan)
class Etoile(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(BLANC)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGEUR)
        self.rect.y = random.randint(0, HAUTEUR)
        self.vitesse = random.randint(1, 3)

    def update(self):
        self.rect.y += self.vitesse
        if self.rect.top > HAUTEUR:
            self.rect.x = random.randint(0, LARGEUR)
            self.rect.y = 0

# Classe pour les missions
class Mission:
    def __init__(self, description, objectif, recompense):
        self.description = description
        self.objectif = objectif
        self.progres = 0
        self.recompense = recompense

    def mettre_a_jour(self, evenement):
        if evenement == self.description.split()[0]:
            self.progres += 1

    def est_complete(self):
        return self.progres >= self.objectif

# Fonction pour dessiner le texte
def dessiner_texte(surface, texte, taille, x, y, couleur=BLANC):
    police = pygame.font.Font(None, taille)
    texte_surface = police.render(texte, True, couleur)
    texte_rect = texte_surface.get_rect()
    texte_rect.midtop = (x, y)
    surface.blit(texte_surface, texte_rect)

# Fonction pour afficher le menu principal
def menu_principal():
    ecran.fill(NOIR)
    dessiner_texte(ecran, "GALAXIA AVANCÉ", 64, LARGEUR // 2, HAUTEUR // 4)
    dessiner_texte(ecran, "1. Commencer", 22, LARGEUR // 2, HAUTEUR // 2)
    dessiner_texte(ecran, "2. Sélection du vaisseau", 22, LARGEUR // 2, HAUTEUR // 2 + 30)
    dessiner_texte(ecran, "3. Quitter", 22, LARGEUR // 2, HAUTEUR // 2 + 60)
    pygame.display.flip()

    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quitter"
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    return "commencer"
                elif event.key == pygame.K_2:
                    return "selection_vaisseau"
                elif event.key == pygame.K_3:
                    return "quitter"

def menu_selection_vaisseau():
    vaisseaux = ['standard', 'rapide', 'puissant']
    index_selection = 0
    points_pimpage = 5

    pimpage = {
        'vitesse': 0,
        'bouclier': 0,
        'puissance_tir': 0
    }

    while True:
        ecran.fill(NOIR)
        dessiner_texte(ecran, "SÉLECTION DU VAISSEAU", 40, LARGEUR // 2, 50)

        for i, vaisseau in enumerate(vaisseaux):
            couleur = VERT if i == index_selection else BLANC
            dessiner_texte(ecran, vaisseau.capitalize(), 30, LARGEUR // 2, 150 + i * 50, couleur)

        dessiner_texte(ecran, f"Points de pimpage: {points_pimpage}", 24, LARGEUR // 2, 300)
        dessiner_texte(ecran, f"Vitesse: {pimpage['vitesse']} [Q]", 20, LARGEUR // 2, 340)
        dessiner_texte(ecran, f"Bouclier: {pimpage['bouclier']} [W]", 20, LARGEUR // 2, 370)
        dessiner_texte(ecran, f"Puissance de tir: {pimpage['puissance_tir']} [E]", 20, LARGEUR // 2, 400)

        dessiner_texte(ecran, "Appuyez sur ESPACE pour confirmer", 24, LARGEUR // 2, HAUTEUR - 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index_selection = (index_selection - 1) % len(vaisseaux)
                elif event.key == pygame.K_DOWN:
                    index_selection = (index_selection + 1) % len(vaisseaux)
                elif event.key == pygame.K_q and points_pimpage > 0:
                    pimpage['vitesse'] += 1
                    points_pimpage -= 1
                elif event.key == pygame.K_w and points_pimpage > 0:
                    pimpage['bouclier'] += 1
                    points_pimpage -= 1
                elif event.key == pygame.K_e and points_pimpage > 0:
                    pimpage['puissance_tir'] += 1
                    points_pimpage -= 1
                elif event.key == pygame.K_SPACE:
                    return vaisseaux[index_selection], pimpage

# Fonction principale du jeu
def jeu_principal(type_vaisseau, pimpage):
    # Création des groupes de sprites
    tous_sprites = pygame.sprite.Group()
    ennemis = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    power_ups = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()
    zones_danger = pygame.sprite.Group()

    # Création du vaisseau du joueur
    vaisseau = Vaisseau(type_vaisseau)
    vaisseau.pimpage = pimpage
    tous_sprites.add(vaisseau)

    # Création des étoiles
    etoiles = pygame.sprite.Group()
    for _ in range(100):
        etoile = Etoile()
        tous_sprites.add(etoile)
        etoiles.add(etoile)

    # Variables du jeu
    score = 0
    niveau = 1
    ressources = 0
    boss = None
    missions = [
        Mission("Détruire 10 ennemis", 10, 50),
        Mission("Collecter 5 power-ups", 5, 100),
        Mission("Survivre 60 secondes", 60, 150)
    ]
    mission_actuelle = missions[0]
    temps_debut = pygame.time.get_ticks()

    # Boucle principale du jeu
    horloge = pygame.time.Clock()
    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    laser = vaisseau.tirer()
                    tous_sprites.add(laser)
                    lasers.add(laser)
                elif event.key == pygame.K_b:
                    vaisseau.utiliser_bouclier()
                elif event.key == pygame.K_n:
                    if vaisseau.utiliser_explosion():
                        for ennemi in ennemis:
                            ennemi.vie = 0

        # Mise à jour
        tous_sprites.update()

        # Génération d'ennemis
        if len(ennemis) < 5 + niveau and random.random() < 0.02:
            ennemi = Ennemi(niveau)
            tous_sprites.add(ennemi)
            ennemis.add(ennemi)

        # Génération de power-ups
        if random.random() < 0.005:
            power_up = PowerUp()
            tous_sprites.add(power_up)
            power_ups.add(power_up)

        # Génération d'astéroïdes
        if random.random() < 0.01:
            asteroide = Asteroide()
            tous_sprites.add(asteroide)
            asteroides.add(asteroide)

        # Génération de zones de danger
        if random.random() < 0.002:
            zone_danger = ZoneDanger()
            tous_sprites.add(zone_danger)
            zones_danger.add(zone_danger)

        # Collisions laser-ennemi
        for laser in lasers:
            ennemis_touches = pygame.sprite.spritecollide(laser, ennemis, False)
            for ennemi in ennemis_touches:
                ennemi.vie -= laser.puissance
                if ennemi.vie <= 0:
                    score += vaisseau.calculer_score(10 * ennemi.niveau)
                    vaisseau.gagner_xp(5 * ennemi.niveau)
                    ennemi.kill()
                    vaisseau.incrementer_combo()
                    mission_actuelle.mettre_a_jour("Détruire")
                laser.kill()

        # Collisions vaisseau-ennemi
        ennemis_touches = pygame.sprite.spritecollide(vaisseau, ennemis, True)
        for ennemi in ennemis_touches:
            vaisseau.bouclier -= 20
            if vaisseau.bouclier <= 0:
                en_cours = False

        # Collisions vaisseau-power-up
        power_ups_touches = pygame.sprite.spritecollide(vaisseau, power_ups, True)
        for power_up in power_ups_touches:
            if power_up.type == 'bouclier':
                vaisseau.bouclier = min(vaisseau.bouclier + 50, 100)
            elif power_up.type == 'vitesse':
                vaisseau.vitesse += 1
            elif power_up.type == 'tir_multiple':
                vaisseau.type_laser = 'rapide'
            mission_actuelle.mettre_a_jour("Collecter")

        # Collisions vaisseau-astéroïde
        asteroides_touches = pygame.sprite.spritecollide(vaisseau, asteroides, True)
        for asteroide in asteroides_touches:
            ressources += asteroide.ressources

        # Dégâts des zones de danger
        if pygame.sprite.spritecollide(vaisseau, zones_danger, False):
            vaisseau.bouclier -= 0.1

        # Gestion du boss
        if boss:
            lasers_boss = boss.tirer()
            for laser in lasers_boss:
                tous_sprites.add(laser)
                lasers.add(laser)

            if pygame.sprite.collide_rect(vaisseau, boss):
                vaisseau.bouclier -= 1

            boss_touche = pygame.sprite.spritecollide(boss, lasers, True)
            for laser in boss_touche:
                boss.vie -= laser.puissance
                if boss.vie <= 0:
                    score += 1000 * niveau
                    boss = None
                    niveau += 1

        # Vérification de la mission actuelle
        if mission_actuelle.est_complete():
            score += mission_actuelle.recompense
            missions.remove(mission_actuelle)
            if missions:
                mission_actuelle = random.choice(missions)
            else:
                mission_actuelle = None

        # Mise à jour du temps pour la mission de survie
        temps_ecoule = (pygame.time.get_ticks() - temps_debut) // 1000
        if mission_actuelle and mission_actuelle.description.startswith("Survivre"):
            mission_actuelle.progres = temps_ecoule

        # Apparition du boss
        if score >= niveau * 1000 and not boss:
            boss = Boss(niveau)
            tous_sprites.add(boss)

        # Dessin
        ecran.fill(NOIR)
        tous_sprites.draw(ecran)

        # Affichage du score, du niveau et du bouclier
        dessiner_texte(ecran, f"Score: {score}", 18, 50, 10)
        dessiner_texte(ecran, f"Niveau: {niveau}", 18, LARGEUR // 2, 10)
        dessiner_texte(ecran, f"Bouclier: {int(vaisseau.bouclier)}", 18, LARGEUR - 70, 10)
        dessiner_texte(ecran, f"Ressources: {ressources}", 18, LARGEUR - 70, 30)

        # Affichage de la mission actuelle
        if mission_actuelle:
            dessiner_texte(ecran,
                           f"Mission: {mission_actuelle.description} ({mission_actuelle.progres}/{mission_actuelle.objectif})",
                           18, LARGEUR // 2, HAUTEUR - 30)

        pygame.display.flip()
        horloge.tick(60)

    return score

# Boucle principale du programme
if __name__ == "__main__":
    while True:
        choix = menu_principal()
        if choix == "commencer":
            type_vaisseau, pimpage = menu_selection_vaisseau()
            if type_vaisseau:
                score_final = jeu_principal(type_vaisseau, pimpage)
                ecran.fill(NOIR)
                dessiner_texte(ecran, f"Game Over - Score: {score_final}", 40, LARGEUR // 2, HAUTEUR // 2)
                pygame.display.flip()
                pygame.time.wait(3000)
        elif choix == "selection_vaisseau":
            menu_selection_vaisseau()
        elif choix == "quitter":
            break

pygame.quit()
