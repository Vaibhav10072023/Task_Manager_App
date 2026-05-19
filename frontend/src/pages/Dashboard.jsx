import React, { useState, useEffect } from 'react';
import { Plus, Calendar, Clock, CheckCircle2, AlertCircle, Eye, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tasksRes, projectsRes] = await Promise.all([
        api.get('/tasks/'),
        api.get('/projects/')
      ]);
      setTasks(tasksRes.data);
      setProjects(projectsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await api.post('/projects/', { name: newProjectName, description: newProjectDesc });
      setShowProjectModal(false);
      setNewProjectName('');
      setNewProjectDesc('');
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Failed to create project');
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await api.put(`/tasks/${taskId}`, { status: newStatus });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    } catch (err) {
      console.error(err);
      alert('Failed to update task status');
    }
  };

  const handleDeleteProject = async (e, projectId) => {
    e.stopPropagation();
    if (!window.confirm('WARNING: Are you sure you want to permanently delete this project and all its tasks? This action cannot be undone.')) return;
    try {
      await api.delete(`/projects/${projectId}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Failed to delete project');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.delete(`/tasks/${taskId}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Failed to delete task');
    }
  };


  const isOverdue = (task) => {
    if (!task.due_date || task.status === 'done') return false;
    return new Date(task.due_date) < new Date();
  };

  const totalTasks = tasks.length;
  const pendingTasks = tasks.filter(t => t.status !== 'done').length;
  const completedTasks = tasks.filter(t => t.status === 'done').length;
  const overdueTasksCount = tasks.filter(t => isOverdue(t)).length;

  const filteredTasks = tasks.filter(task => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'overdue') return isOverdue(task);
    return task.status === filterStatus;
  });

  if (loading) return <div className="page-container" style={{textAlign: 'center', marginTop: '10vh'}}>Loading...</div>;

  return (
    <div className="page-container">
      <div className="header-actions">
        <div>
          <h2>Welcome back, {user?.name}</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>Here is a simple overview of your team's work.</p>
        </div>
        {user?.role === 'admin' && (
          <button className="btn" onClick={() => setShowProjectModal(true)}>
            <Plus size={16} /> New Project
          </button>
        )}
      </div>

      <div className="stats-grid">
        <div className="card glass-panel stat-card">
          <span className="stat-num">{totalTasks}</span>
          <span className="stat-label">Total Tasks</span>
        </div>
        <div className="card glass-panel stat-card">
          <span className="stat-num text-warning">{pendingTasks}</span>
          <span className="stat-label">Pending Tasks</span>
        </div>
        <div className="card glass-panel stat-card">
          <span className="stat-num text-success">{completedTasks}</span>
          <span className="stat-label">Completed Tasks</span>
        </div>
        <div className="card glass-panel stat-card">
          <span className="stat-num text-danger">{overdueTasksCount}</span>
          <span className="stat-label">Overdue Tasks</span>
        </div>
      </div>

      <div style={{ marginBottom: '3rem' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>Your Collaborative Projects</h3>
        <div className="grid">
          {projects.map(project => (
            <div key={project.id} className="card glass-panel project-card" onClick={() => navigate(`/projects/${project.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <h4 className="card-title" style={{ margin: 0 }}>{project.name}</h4>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn btn-outline" style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}>
                    <Eye size={12} /> View
                  </button>
                  {isAdmin && (
                    <button 
                      onClick={(e) => handleDeleteProject(e, project.id)}
                      className="remove-member-btn" 
                      style={{ 
                        background: 'rgba(239, 68, 68, 0.1)', 
                        color: 'var(--danger)', 
                        padding: '0.35rem', 
                        borderRadius: '6px', 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        border: '1px solid rgba(239, 68, 68, 0.2)'
                      }}
                      title="Delete Project"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
              </div>
              <p className="card-desc" style={{ minHeight: '40px' }}>{project.description}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
                <span>Owner: {project.owner?.name}</span>
                <span>{project.members?.length || 0} Members</span>
              </div>
            </div>
          ))}

          {projects.length === 0 && (
            <div className="card glass-panel" style={{ gridColumn: '1/-1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              No projects found. {user?.role === 'admin' ? 'Click "New Project" to start!' : 'Ask your admin to add you to a project.'}
            </div>
          )}
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3>Task Status & Assignment</h3>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Filter status:</label>
            <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ width: 'auto', padding: '0.5rem 1rem' }}>
              <option value="all">All Tasks</option>
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
              <option value="overdue">Overdue Only</option>
            </select>
          </div>
        </div>

        <div className="task-list">
          {filteredTasks.map(task => {
            const taskIsOverdue = isOverdue(task);
            const taskProject = projects.find(p => p.id === task.project_id);
            return (
              <div key={task.id} className="card glass-panel task-row">
                <div className="task-info">
                  <div className="task-row-title">
                    {task.title}
                    {taskIsOverdue && <span className="badge overdue">Overdue</span>}
                    <span className={`badge ${task.status}`}>{task.status.replace('_', ' ')}</span>
                  </div>
                  <p className="task-row-desc">{task.description}</p>
                  {taskProject && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 500, marginTop: '0.25rem', display: 'inline-block' }}>
                      Project: {taskProject.name}
                    </span>
                  )}
                </div>

                <div className="task-meta">
                  {task.due_date && (
                    <div className={`task-date ${taskIsOverdue ? 'overdue' : ''}`}>
                      <Calendar size={14} />
                      {new Date(task.due_date).toLocaleDateString()}
                    </div>
                  )}
                  {task.assignee && (
                    <div className="task-assignee">
                      Assignee: {task.assignee.name}
                    </div>
                  )}
                  <div>
                    {task.assigned_to === user?.id ? (

                      <select 
                        value={task.status} 
                        onChange={e => handleStatusChange(task.id, e.target.value)}
                        style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem', background: 'rgba(30,41,59,0.9)', width: 'auto' }}
                      >
                        <option value="todo">To Do</option>
                        <option value="in_progress">In Progress</option>
                        <option value="done">Done</option>
                      </select>
                    ) : (
                      <span className={`badge ${task.status}`}>{task.status.replace('_', ' ')}</span>
                    )}
                  </div>

                  {isAdmin && (
                    <button 
                      onClick={() => handleDeleteTask(task.id)} 
                      className="remove-member-btn" 
                      style={{ 
                        background: 'rgba(239, 68, 68, 0.1)', 
                        color: 'var(--danger)', 
                        padding: '0.4rem', 
                        borderRadius: '6px', 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        border: '1px solid rgba(239, 68, 68, 0.2)'
                      }}
                      title="Delete Task"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}

                </div>
              </div>
            );
          })}
          {filteredTasks.length === 0 && (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No tasks matching this status.</p>
          )}
        </div>
      </div>

      {showProjectModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ padding: '2rem', width: '90%', maxWidth: '400px', maxHeight: '90vh', overflowY: 'auto' }}>

            <h3 style={{ marginBottom: '1rem' }}>Create New Project</h3>
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label>Project Name</label>
                <input required value={newProjectName} onChange={e => setNewProjectName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea required value={newProjectDesc} onChange={e => setNewProjectDesc(e.target.value)} />
              </div>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowProjectModal(false)}>Cancel</button>
                <button type="submit" className="btn">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

