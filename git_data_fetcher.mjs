import { fetch } from "undici";
import fs from "fs";
import dotenv from "dotenv";

dotenv.config();

const openSource = {
  githubConvertedToken: "replace",
  githubUserName: "replace",
};

// Log environment variables to verify
console.log("GitHub Token:", openSource.githubConvertedToken);
console.log("GitHub Username:", openSource.githubUserName);

const query_pr = {
  query: `
  query {
    user(login: "${openSource.githubUserName}"){
      pullRequests(last: 100, orderBy: {field: CREATED_AT, direction: DESC}){
      totalCount
      nodes{
        id
        title
        url
        state
        mergedBy {
            avatarUrl
            url
            login
        }
        createdAt
        number
        changedFiles
        additions
        deletions
        baseRepository {
            name
            url
            owner {
              avatarUrl
              login
              url
            }
          }
      }
    }
  }
}
  `,
};

const query_issue = {
  query: `
  query {
    user(login: "${openSource.githubUserName}") {
    issues(last: 100, orderBy: {field:CREATED_AT, direction: DESC}){
      totalCount
      nodes{
        id
        closed
        title
        createdAt
        url
        number
        assignees(first:100){
          nodes{
            avatarUrl
            name
            url
          }
        }
        repository{
          name
          url
          owner{
            login
            avatarUrl
            url
          }
        }
      }
    }
  }
  }
  `,
};

const query_org = {
  query: `
  query {
    user(login: "${openSource.githubUserName}") {
      repositoriesContributedTo(last: 100){
        totalCount
        nodes{
          owner{
            login
            avatarUrl
            __typename
          }
        }
      }
    }
  }
  `,
};

const query_pinned_projects = {
  query: `
  query { 
    user(login: "${openSource.githubUserName}") { 
      pinnedItems(first: 6, types: REPOSITORY) {
        totalCount
        nodes{
          ... on Repository{
            id
              name
              createdAt,
              url,
              description,
              isFork,
              languages(first:10){
                nodes{
                  name
                }
              }
          }
        }
      }
    }
  }
  `,
};

const baseUrl = "https://api.github.com/graphql";

const headers = {
  "Content-Type": "application/json",
  Authorization: "bearer " + openSource.githubConvertedToken,
};

// Ensure directory exists before writing files
if (!fs.existsSync("./src/shared/opensource/")) {
  fs.mkdirSync("./src/shared/opensource/", { recursive: true });
}

// Function to handle fetch and file writing
const fetchData = (query, fileName, processData) => {
  fetch(baseUrl, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(query),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `GitHub API error: ${response.status} ${response.statusText}`,
        );
      }
      return response.text();
    })
    .then((txt) => {
      const data = JSON.parse(txt);
      const processedData = processData(data);
      console.log(`Fetching the ${fileName} Data.\n`);
      fs.writeFile(
        `./src/shared/opensource/${fileName}.json`,
        JSON.stringify(processedData),
        function (err) {
          if (err) {
            console.log(err);
          }
        },
      );
    })
    .catch((error) =>
      console.log(
        `Error occurred during fetching ${fileName} data`,
        JSON.stringify(error),
      ),
    );
};

// Fetch pull requests
fetchData(query_pr, "pull_requests", (data) => {
  const cropped = { data: data["data"]["user"]["pullRequests"]["nodes"] };
  let open = 0,
    closed = 0,
    merged = 0;
  cropped.data.forEach((pr) => {
    if (pr.state === "OPEN") open++;
    else if (pr.state === "MERGED") merged++;
    else closed++;
  });
  cropped.open = open;
  cropped.closed = closed;
  cropped.merged = merged;
  cropped.totalCount = cropped.data.length;
  return cropped;
});

// Fetch issues
fetchData(query_issue, "issues", (data) => {
  const cropped = { data: data["data"]["user"]["issues"]["nodes"] };
  let open = 0,
    closed = 0;
  cropped.data.forEach((issue) => {
    if (!issue.closed) open++;
    else closed++;
  });
  cropped.open = open;
  cropped.closed = closed;
  cropped.totalCount = cropped.data.length;
  return cropped;
});

// Fetch contributed organizations
fetchData(query_org, "organizations", (data) => {
  const orgs = data["data"]["user"]["repositoriesContributedTo"]["nodes"];
  const newOrgs = { data: [] };
  orgs.forEach((org) => {
    if (
      org.owner.__typename === "Organization" &&
      !newOrgs.data.some((o) => JSON.stringify(o) === JSON.stringify(org.owner))
    ) {
      newOrgs.data.push(org.owner);
    }
  });
  return newOrgs;
});

// Fetch pinned projects
const languages_icons = {
  Python: "logos-python",
  "Jupyter Notebook": "logos-jupyter",
  HTML: "logos-html-5",
  CSS: "logos-css-3",
  JavaScript: "logos-javascript",
  "C#": "logos-c-sharp",
  Java: "logos-java",
  Shell: "simple-icons:shell",
  Ruby: "logos:ruby",
  PHP: "logos-php",
  Dockerfile: "simple-icons:docker",
  Rust: "logos-rust",
};

fetchData(query_pinned_projects, "projects", (data) => {
  const projects = data["data"]["user"]["pinnedItems"]["nodes"];
  const newProjects = { data: [] };
  projects.forEach((project) => {
    const languages = project.languages.nodes.map((lang) => ({
      name: lang.name,
      iconifyClass: languages_icons[lang.name] || "",
    }));
    newProjects.data.push({ ...project, languages });
  });
  return newProjects;
});
