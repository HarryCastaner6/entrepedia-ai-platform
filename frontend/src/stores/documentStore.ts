import { create } from 'zustand';

interface ProcessedDocument {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  processed_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  embedding_count?: number;
  content_preview?: string;
  metadata?: {
    page_count?: number;
    duration?: number;
    title?: string;
    author?: string;
  };
}

interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
}

interface DocumentStats {
  total_documents: number;
  total_size: number;
  total_embeddings: number;
  processed_today: number;
}

interface DocumentState {
  // State
  documents: ProcessedDocument[];
  uploadProgress: { [filename: string]: UploadProgress };
  stats: DocumentStats | null;
  isLoading: boolean;
  searchQuery: string;
  filteredDocuments: ProcessedDocument[];

  // Actions
  setDocuments: (documents: ProcessedDocument[]) => void;
  addDocument: (document: ProcessedDocument) => void;
  updateDocument: (id: string, updates: Partial<ProcessedDocument>) => void;
  removeDocument: (id: string) => void;
  setUploadProgress: (filename: string, progress: UploadProgress) => void;
  clearUploadProgress: (filename: string) => void;
  setStats: (stats: DocumentStats) => void;
  setLoading: (loading: boolean) => void;
  setSearchQuery: (query: string) => void;
  filterDocuments: (query?: string) => void;
  clearDocuments: () => void;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  // Initial state
  documents: [],
  uploadProgress: {},
  stats: null,
  isLoading: false,
  searchQuery: '',
  filteredDocuments: [],

  // Actions
  setDocuments: (documents: ProcessedDocument[]) => {
    set({ documents });
    get().filterDocuments();
  },

  addDocument: (document: ProcessedDocument) => {
    const currentDocs = get().documents;
    const updatedDocs = [document, ...currentDocs];
    set({ documents: updatedDocs });
    get().filterDocuments();
  },

  updateDocument: (id: string, updates: Partial<ProcessedDocument>) => {
    const currentDocs = get().documents;
    const updatedDocs = currentDocs.map(doc =>
      doc.id === id ? { ...doc, ...updates } : doc
    );
    set({ documents: updatedDocs });
    get().filterDocuments();
  },

  removeDocument: (id: string) => {
    const currentDocs = get().documents;
    const updatedDocs = currentDocs.filter(doc => doc.id !== id);
    set({ documents: updatedDocs });
    get().filterDocuments();
  },

  setUploadProgress: (filename: string, progress: UploadProgress) => {
    const currentProgress = get().uploadProgress;
    set({
      uploadProgress: {
        ...currentProgress,
        [filename]: progress
      }
    });
  },

  clearUploadProgress: (filename: string) => {
    const currentProgress = get().uploadProgress;
    const { [filename]: removed, ...remaining } = currentProgress;
    set({ uploadProgress: remaining });
  },

  setStats: (stats: DocumentStats) => {
    set({ stats });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
    get().filterDocuments(query);
  },

  filterDocuments: (query?: string) => {
    const searchQuery = query !== undefined ? query : get().searchQuery;
    const documents = get().documents;

    if (!searchQuery.trim()) {
      set({ filteredDocuments: documents });
      return;
    }

    const filtered = documents.filter(doc =>
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.file_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.content_preview?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.metadata?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.metadata?.author?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    set({ filteredDocuments: filtered });
  },

  clearDocuments: () => {
    set({
      documents: [],
      uploadProgress: {},
      stats: null,
      searchQuery: '',
      filteredDocuments: []
    });
  }
}));