/* Change this file to get your personal Porfolio */

// Website related settings
const settings = {
  isSplash: false, // Change this to false if you don't want Splash screen.
};

const description =
  "Ein leidenschaftlicher Mensch, der gerne seine Fähigkeiten in der Softwareentwicklung einsetzt und ständig dazulernt.";
//SEO Related settings
const seo = {
  title: "Manuel Schüleins Portfolio",
  description: description,
  og: {
    title: "Maneul Schülein Portfolio",
    type: "website",
    url: "https://deadmade.github.io",
  },
};

//Home Page
const greeting = {
  title: "Manuel Schülein",
  logo_name: "Manuel",
  nickname: "",
  subTitle: description,
  resumeLink: "",
  portfolio_repository: "https://github.com/deadmade",
  githubProfile: "https://github.com/deadmade",
};

const socialMediaLinks = [
  {
    name: "Github",
    link: "https://github.com/deadmade",
    fontAwesomeIcon: "fa-github", // Reference https://fontawesome.com/icons/github?style=brands
    backgroundColor: "#181717", // Reference https://simpleicons.org/?q=github
  },
  {
    name: "LinkedIn",
    link: "www.linkedin.com/in/manuel-schülein-408421247",
    fontAwesomeIcon: "fa-linkedin-in", // Reference https://fontawesome.com/icons/linkedin-in?style=brands
    backgroundColor: "#0077B5", // Reference https://simpleicons.org/?q=linkedin
  },
  {
    name: "Email",
    link: "mailto:manuel.schuelein@proton.me",
    fontAwesomeIcon: "fas fa-envelope", // Reference https://fontawesome.com/icons/google?style=brands
    backgroundColor: "#8B4DFF", // Reference https://simpleicons.org/?q=gmail
  },
  {
    name: "Discord",
    link: "https://discord.com/users/819908750814347275",
    fontAwesomeIcon: "fa-discord", // Reference https://fontawesome.com/icons/google?style=brands
    backgroundColor: "#5865F2", // Reference https://simpleicons.org/?q=gmail
  },
];

const skills = {
  data: [
    {
      title: "C# Backend Development",
      fileName: "BackendDevImg",
      skills: [
        "⚡ Entwicklung von Backend-Lösungen mit C# ",
        "⚡ Erstellung und Integration von APIs",
        "⚡ Schreiben von optimierten SQL-Abfragen",
      ],
      softwareSkills: [
        {
          skillName: "C#",
          fontAwesomeClassname: "simple-icons:csharp",
          style: {
            color: "#9B4993",
          },
        },
        {
          skillName: "Blazor",
          fontAwesomeClassname: "simple-icons:blazor",
          style: {
            color: "#512BD4",
          },
        },
        {
          skillName: "TSQL",
          fontAwesomeClassname: "fa-database",
          style: {
            color: "#A91D22",
          },
        },
      ],
    },
    {
      title: "Sage100 Entwicklung",
      fileName: "DesignImg",
      skills: [
        "⚡ Entwicklung von SData Apis",
        "⚡ Erstellung von Sage100 Erweiterungen",
        "⚡ Implementierung von Appdesigner Masken",
        "⚡ Erweiterung von Sage100 Standardmasken",
      ],
      softwareSkills: [
        {
          skillName: "Sage100",
          fontAwesomeClassname: "simple-icons:sage",
          style: {
            color: "#00D639",
          },
        },
      ],
    },
    {
      title: "Tools I Enjoy Using",
      fileName: "DataScienceImg",
      skills: ["⚡ Vim Motions", "⚡ JetBrains IDEs", "⚡ Git Version Control"],
      softwareSkills: [
        {
          skillName: "Vim Motions",
          fontAwesomeClassname: "simple-icons:vim",
          style: {
            color: "#019733",
          },
        },
        {
          skillName: "JetBrains Rider",
          fontAwesomeClassname: "simple-icons:rider",
          style: {
            color: "#000000",
          },
        },
        {
          skillName: "Git",
          fontAwesomeClassname: "simple-icons:git",
          style: {
            color: "#F1502F",
          },
        },
      ],
    },
  ],
};

// Education Page
const competitiveSites = {
  competitiveSites: [],
};

const degrees = {
  degrees: [
    {
      title: "DHBW Heidenheim",
      subtitle: "Bachelor of Science in Allgemeine Informatik",
      logo_path: "DHBW-Logo.png",
      alt_name: "DHBW Heidenheim",
      duration: "2023 - now",
      descriptions: [
        "Ich bin ein dualer Student im 3. Semester an der DHBW Heidenheim. Aktuell studiere ich Allgemeine Informatik. In meinem Studium lerne ich die Grundlagen der Informatik und vertiefe mein Wissen in verschiedenen Bereichen.",
      ],
      website_link: "https://www.heidenheim.dhbw.de/startseite",
    },
    {
      title: "Berufsoberschule Donauwörth",
      subtitle: "Fachabitur Technik",
      logo_path: "fosboslogo.png",
      alt_name: "FOS BOS Donauwörth",
      duration: "2022 - 2023",
      descriptions: [
        "Um ein Studium an der DHBW Heidenheim zu beginnen, habe ich mein Fachabitur an der FOS BOS Donauwörth absolviert.",
      ],
      website_link: "https://www.fosbos-donauwoerth.de/",
    },
  ],
};

const certifications = {
  certifications: [],
};

const books = {
  books: [
    {
      title: "Understanding the Digital World",
      subtitle: "by Brian W. Kernighan",
      logo_path: "UnderstandingTheDigitalWorld.jpg",
      alt_name: "Understanding the Digital World - Brian W. Kernighan",
      book_link:
        "https://www.amazon.de/Understanding-Digital-World-Computers-Internet-dp-0691219095/dp/0691219095/ref=dp_ob_title_bk",
      color_code: "#8C151599",
    },
    {
      title: "The C Programming Language",
      subtitle: "by Brian W. Kernighan and Dennis M. Ritchie",
      logo_path: "TheCProgrammingLanguage.jpg",
      alt_name: "The C Programming Language - Brian W. Kernighan",
      book_link:
        "https://www.amazon.com/Programming-Language-2nd-Brian-Kernighan/dp/0131103628",
      color_code: "#8C151599",
    },
    {
      title: "Cyber-Sicherheit",
      subtitle: "von Norbert Pohlmann",
      logo_path: "CyberSicherheit.jpg",
      alt_name: "Cyber-Sicherheit - Norbert Pohlmann",
      book_link:
        "https://www.amazon.de/Cyber-Sicherheit-Architekturen-Eigenschaften-Cyber-Sicherheitssystemen-Digitalisierung/dp/3658253975",
      color_code: "#8C151599",
    },
  ],
};

// Experience Page
const experience = {
  title: "Experience",
  subtitle: "Arbeits- und Ausbildungserfahrung",
  description:
    "Bisher habe ich Erfahrungen in der Softwareentwicklung durch meine Ausbildung zum Fachinformatiker für Anwendungsentwicklung und mein duales Studium bei 4SELLERS gesammelt.",
  header_image_path: "experience.svg",
  sections: [
    {
      title: "Arbeitserfahrung",
      work: "false",
      experiences: [
        {
          title: "Dualer Studium Allgemeine Informatik",
          company: "4SELLERS GmbH",
          company_url: "https://www.4sellers.de/",
          logo_path: "4sellers.png",
          duration: "Oktober 2023 - now",
          location: "Rain am Lech, Bayern, Deutschland",
          description:
            "Nach der erfolgreich Bestandenen Fachabiturprüfung habe ich ein duales Studium bei 4SELLERS begonnen. Derzeit bin ich im Bereich ERP Custom Development tätig. Meine Hauptaufgabe ist es, das Sage ERP-System zu erweitern und anzupassen, um kundenspezifische Lösungen zu implementieren und Geschäftsprozesse zu optimieren. In dieser Funktion arbeite ich intensiv mit T-SQL Datenbanken und programmiere in C# unter Verwendung des .NET Frameworks.",
          color: "#000000",
        },
        {
          title: "Ausbildung zum Fachinformtiker Anwendungsentwicklung",
          company: "4SELLERS GmbH",
          company_url: "https://www.4sellers.de/",
          logo_path: "4sellers.png",
          duration: "September 2019 - July 2022",
          location: "Rain am Lech, Bayern, Deutschland",
          description:
            "Meine Ausbildung zum Fachinformatiker für Anwendungsentwicklung bei 4SELLERS habe ich erfolgreich abgeschlossen. Dabei habe ich wertvolle praktische Erfahrungen in der Entwicklung von Visual Studio Extensions, der Arbeit mit dem .NET Framework, C# und der Implementierung von WPF-Anwendungen gesammelt.",
          color: "#000000",
        },
      ],
    },
  ],
};

// Projects Page
const projectsHeader = {
  title: "Projects",
  description:
    "Meine Projekte, die ich in meiner Freizeit bzw für mein Studium entwickelt habe.",
  avatar_image_path: "projects_image.svg",
};

const publicationsHeader = {
  title: "",
  description: "",
  avatar_image_path: "",
};

const publications = {
  data: [],
};

// Contact Page
const contactPageData = {
  contactSection: {
    title: "Contact Me",
    profile_image_path: "animated_ashutosh.png",
    description:
      "I am available on almost every social media. You can message me, I will reply within 24 hours. I can help you with ML, AI, React, Android, Cloud and Opensource Development.",
  },
  blogSection: {},
  addressSection: {},
  phoneSection: {},
};

export {
  settings,
  seo,
  greeting,
  socialMediaLinks,
  skills,
  competitiveSites,
  degrees,
  certifications,
  experience,
  projectsHeader,
  publicationsHeader,
  publications,
  contactPageData,
  books,
};
