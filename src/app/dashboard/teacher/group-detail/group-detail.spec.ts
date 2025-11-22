import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Group-detail } from './group-detail';

describe('Group-detail', () => {
  let component: Group-detail;
  let fixture: ComponentFixture<Group-detail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Group-detail,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Group-detail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
