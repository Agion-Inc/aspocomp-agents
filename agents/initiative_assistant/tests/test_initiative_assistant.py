"""Unit tests for Initiative Assistant Agent."""

import unittest
import os
import sys
import tempfile
import shutil

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.initiative_assistant.agent import InitiativeAssistantAgent
from agents.initiative_assistant.config import AGENT_CONFIG
from agents.initiative_assistant.database import InitiativeDatabase
from agents.initiative_assistant.models import Initiative
from agents.initiative_assistant import tools


class TestInitiativeAssistantAgent(unittest.TestCase):
    """Test cases for Initiative Assistant Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = InitiativeAssistantAgent(AGENT_CONFIG)
        # Use temporary database for tests
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, 'test_initiatives.db')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.agent_id, "initiative_assistant")
        self.assertEqual(self.agent.name, "Initiative Assistant")
        self.assertTrue(self.agent.is_enabled())
    
    def test_get_capabilities(self):
        """Test agent returns capabilities."""
        capabilities = self.agent.get_capabilities()
        self.assertIn("agent_id", capabilities)
        self.assertIn("name", capabilities)
        self.assertIn("description", capabilities)
        self.assertIn("tools", capabilities)
        self.assertEqual(capabilities["agent_id"], "initiative_assistant")
    
    def test_system_prompt_loading(self):
        """Test system prompt loads correctly."""
        prompt = self.agent.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("Initiative Assistant", prompt)
    
    def test_build_tools(self):
        """Test tools are built correctly."""
        agent_tools = self.agent.build_tools()
        self.assertIsInstance(agent_tools, list)
        self.assertGreater(len(agent_tools), 0)
    
    def test_database_initialization(self):
        """Test database initializes correctly."""
        db = InitiativeDatabase(self.test_db_path)
        self.assertIsNotNone(db)
        self.assertTrue(os.path.exists(self.test_db_path))
    
    def test_save_and_get_initiative(self):
        """Test saving and retrieving initiative."""
        db = InitiativeDatabase(self.test_db_path)
        
        initiative = Initiative(
            title="Test Initiative",
            description="Test description",
            creator_name="Test User",
            goals="Test goals"
        )
        
        initiative_id = db.save_initiative(initiative)
        self.assertIsNotNone(initiative_id)
        
        retrieved = db.get_initiative(initiative_id, include_personal=False)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test Initiative")
        self.assertEqual(retrieved.description, "Test description")
        # Verify personal info is excluded from dict representation
        data_dict = retrieved.to_dict(include_personal=False)
        self.assertNotIn("creator_name", data_dict)
        self.assertNotIn("creator_email", data_dict)
        self.assertNotIn("creator_contact", data_dict)
    
    def test_search_similar_initiatives(self):
        """Test searching for similar initiatives."""
        db = InitiativeDatabase(self.test_db_path)
        
        # Save a test initiative
        initiative1 = Initiative(
            title="Automate Work Instructions",
            description="Automate work instruction updates",
            creator_name="User 1"
        )
        db.save_initiative(initiative1)
        
        # Search for similar
        similar = db.search_similar("Work Instructions Automation", "Automate updates", limit=5)
        self.assertIsInstance(similar, list)
        self.assertGreater(len(similar), 0)
    
    def test_tool_save_initiative(self):
        """Test save_initiative tool."""
        # Temporarily override database path
        original_path = AGENT_CONFIG["database"]["path"]
        AGENT_CONFIG["database"]["path"] = self.test_db_path
        
        try:
            result = tools.save_initiative(
                title="Test Initiative",
                description="Test description",
                creator_name="Test User"
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("initiative_id", result)
        finally:
            AGENT_CONFIG["database"]["path"] = original_path
    
    def test_tool_search_similar(self):
        """Test search_similar_initiatives tool."""
        # Temporarily override database path
        original_path = AGENT_CONFIG["database"]["path"]
        AGENT_CONFIG["database"]["path"] = self.test_db_path
        
        try:
            # First save an initiative
            db = InitiativeDatabase(self.test_db_path)
            initiative = Initiative(
                title="Test Initiative",
                description="Test description",
                creator_name="Test User"
            )
            db.save_initiative(initiative)
            
            # Then search
            result = tools.search_similar_initiatives("Test Initiative")
            
            self.assertTrue(result.get("success"))
            self.assertIn("similar_initiatives", result)
        finally:
            AGENT_CONFIG["database"]["path"] = original_path


if __name__ == '__main__':
    unittest.main()

