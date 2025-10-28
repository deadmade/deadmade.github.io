#!/usr/bin/env node

/**
 * Fetch pinned GitHub repositories and save to data/projects.json
 * This script runs during the GitHub Actions build process to keep projects up-to-date
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
const GITHUB_USERNAME = process.env.GITHUB_USERNAME || 'deadmade'; // Default username

// GraphQL query to fetch pinned repositories
const QUERY = `
query($username: String!) {
  user(login: $username) {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          description
          url
          homepageUrl
          stargazerCount
          forkCount
          primaryLanguage {
            name
            color
          }
          repositoryTopics(first: 10) {
            nodes {
              topic {
                name
              }
            }
          }
          updatedAt
          createdAt
          pushedAt
        }
      }
    }
  }
}
`;

/**
 * Make GraphQL request to GitHub API
 */
function fetchGitHubData(username, token) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      query: QUERY,
      variables: { username }
    });

    const options = {
      hostname: 'api.github.com',
      port: 443,
      path: '/graphql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
        'User-Agent': 'Hugo-Projects-Fetcher',
        ...(token && { 'Authorization': `bearer ${token}` })
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error(`GitHub API returned status ${res.statusCode}: ${responseData}`));
          return;
        }

        try {
          const json = JSON.parse(responseData);
          if (json.errors) {
            reject(new Error(`GraphQL errors: ${JSON.stringify(json.errors)}`));
            return;
          }
          resolve(json);
        } catch (err) {
          reject(new Error(`Failed to parse response: ${err.message}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.write(data);
    req.end();
  });
}

/**
 * Transform GitHub API response to our project format
 */
function transformProjects(response) {
  if (!response.data || !response.data.user || !response.data.user.pinnedItems) {
    throw new Error('Unexpected API response structure');
  }

  const repositories = response.data.user.pinnedItems.nodes;

  return repositories.map(repo => ({
    name: repo.name,
    description: repo.description || '',
    url: repo.url,
    homepage: repo.homepageUrl || null,
    stars: repo.stargazerCount,
    forks: repo.forkCount,
    language: repo.primaryLanguage ? {
      name: repo.primaryLanguage.name,
      color: repo.primaryLanguage.color
    } : null,
    topics: repo.repositoryTopics.nodes.map(node => node.topic.name),
    updatedAt: repo.updatedAt,
    createdAt: repo.createdAt,
    pushedAt: repo.pushedAt
  }));
}

/**
 * Main execution
 */
async function main() {
  try {
    console.log('Fetching pinned repositories from GitHub...');
    console.log(`Username: ${GITHUB_USERNAME}`);

    if (!GITHUB_TOKEN) {
      console.warn('Warning: No GitHub token provided. API rate limits will be restricted.');
      console.warn('Set GITHUB_TOKEN or GH_TOKEN environment variable for higher limits.');
    }

    // Fetch data from GitHub
    const response = await fetchGitHubData(GITHUB_USERNAME, GITHUB_TOKEN);

    // Transform to our format
    const projects = transformProjects(response);

    console.log(`Successfully fetched ${projects.length} pinned repositories`);

    // Ensure data directory exists
    const dataDir = path.join(__dirname, '..', 'data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
      console.log('Created data directory');
    }

    // Write to data/projects.json
    const outputPath = path.join(dataDir, 'projects.json');
    fs.writeFileSync(outputPath, JSON.stringify(projects, null, 2), 'utf8');

    console.log(`✓ Projects data written to ${outputPath}`);

    // Print summary
    projects.forEach((project, index) => {
      console.log(`  ${index + 1}. ${project.name} - ${project.language?.name || 'No language'} - ⭐ ${project.stars}`);
    });

  } catch (error) {
    console.error('Error fetching projects:', error.message);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { fetchGitHubData, transformProjects };
