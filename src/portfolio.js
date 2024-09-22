/* Change this file to get your personal Porfolio */

// Website related settings
const settings = {
  isSplash: false, // Change this to false if you don't want Splash screen.
};

//SEO Related settings
const seo = {
  title: "Manuel Schüleins Portfolio",
  description:
    "A passionate individual who always thrives to work on end to end products which develop sustainable and scalable social and technical systems to create impact.",
  og: {
    title: "Ashutosh Hathidara Portfolio",
    type: "website",
    url: "http://ashutoshhathidara.com/",
  },
};

//Home Page
const greeting = {
  title: "Manuel Schülein",
  logo_name: "deadmade",
  nickname: "",
  subTitle:
    "A passionate individual who always thrives to work on end to end products which develop sustainable and scalable social and technical systems to create impact.",
  resumeLink:
    "https://drive.google.com/file/d/1bXRknv_h-XI_3CQ3SGPteGODtvEb7YvI/view?usp=sharing",
  portfolio_repository: "https://github.com/deadmade",
  githubProfile: "https://github.com/deadmade",
};

const socialMediaLinks = [
  /* Your Social Media Link */
  // github: "https://github.com/ashutosh1919",
  // linkedin: "https://www.linkedin.com/in/ashutosh-hathidara-88710b138/",
  // gmail: "ashutoshhathidara98@gmail.com",
  // gitlab: "https://gitlab.com/ashutoshhathidara98",
  // facebook: "https://www.facebook.com/laymanbrother.19/",
  // twitter: "https://twitter.com/ashutosh_1919",
  // instagram: "https://www.instagram.com/layman_brother/"

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
      descriptions: [""],
      website_link: "https://www.heidenheim.dhbw.de/startseite",
    },
    {
      title: "Berufsoberschule Donauwörth",
      subtitle: "Fachabitur Technik",
      logo_path: "fosboslogo.png",
      alt_name: "FOS BOS Donauwörth",
      duration: "2022 - 2023",
      descriptions: [""],
      website_link: "https://www.fosbos-donauwoerth.de/",
    },
  ],
};

const certifications = {
  certifications: [],
};

// Experience Page
const experience = {
  title: "Experience",
  subtitle: "Work, Internship and Volunteership",
  description:
    "I have worked with many evolving startups as ML and DL Developer, Designer and Software Architect. I have also worked with some well established companies mostly as AI Developer. I love organising events and that is why I am also involved with many opensource communities as a representative.",
  header_image_path: "experience.svg",
  sections: [
    {
      title: "Work",
      work: true,
      experiences: [
        {
          title: "Dualer Studium Allgemeine Informatik",
          company: "4SELLERS GmbH",
          company_url: "https://www.4sellers.de/",
          logo_path: "tiktok_logo.png",
          duration: "Oktober 2023 - now",
          location: "Rain am Lech, Bayern, Deutschland",
          description: "",
          color: "#000000",
        },
        {
          title: "Ausbildung zum Fachinformtiker Anwendungsentwicklung",
          company: "4SELLERS GmbH",
          company_url: "https://www.4sellers.de/",
          logo_path: "tiktok_logo.png",
          duration: "September 2019 - July 2022",
          location: "Rain am Lech, Bayern, Deutschland",
          description: "",
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
    "My projects makes use of vast variety of latest technology tools. My best experience is to create Data Science projects and deploy them to web applications using cloud infrastructure.",
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
};
